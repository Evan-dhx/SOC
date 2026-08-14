import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '10.10.102.220'
USER = 'root'
PASS = 'PP@ssw0rd'

print("=" * 60)
print("综合修复脚本 - protobuf/nfdump/config_pusher/tisrs.conf")
print("=" * 60)

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)
print("连接成功!\n")

def run(cmd, label=None, check=False):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        status = "OK" if not err.strip() else "CHECK"
        print(f"[{label}] {'OK' if not err.strip() else 'STDERR: ' + err.strip()[:200]}")
    return out, err

# ===== 1. 检查 config_pusher 当前状态 =====
print("=" * 40)
print("[1] 检查 config_pusher 当前状态")
print("=" * 40)

out, _ = run('journalctl -t config_pusher --no-pager --since "15:10" 2>/dev/null | wc -l', "config_pusher 15:10后 syslog 条数")
count = out.strip()
print(f"  15:10 后 syslog 条数: {count}")

out, _ = run('journalctl -t config_pusher --no-pager -n 5 2>/dev/null', "config_pusher 最近5条")
print(f"  最近5条:")
print(out.strip() if out.strip() else "  (无)")

# 检查 config_pusher 是否能正常运行
out, _ = run('LD_LIBRARY_PATH= /Server/bin/config_pusher 2>&1; echo "EXIT_CODE=$?"', "config_pusher 测试运行")
exit_match = [l for l in out.split('\n') if 'EXIT_CODE' in l]
if exit_match:
    exit_code = exit_match[0].split('=')[1].strip()
    print(f"  退出码: {exit_code}")
    if 'symbol lookup error' in out.lower():
        print("  [!] config_pusher 仍有 symbol lookup error!")
    elif exit_code == '0':
        print("  config_pusher 正常运行!")
    else:
        print(f"  config_pusher 退出码 {exit_code} (可能有数据库错误)")

# ===== 2. 修复 nfdump protobuf =====
print("\n" + "=" * 40)
print("[2] 修复 nfdump protobuf 符号不兼容")
print("=" * 40)

# 创建旧库兼容目录
run('mkdir -p /usr/local/lib/compat', "创建 compat 目录")

# 复制旧库
run('cp /usr/local/lib/libprotobuf.so.19.0.0.bak.old /usr/local/lib/compat/libprotobuf.so.19.0.0', "复制旧库")
run('ln -sf libprotobuf.so.19.0.0 /usr/local/lib/compat/libprotobuf.so.19', "创建 compat 软链接")
run('ln -sf libprotobuf.so.19.0.0 /usr/local/lib/compat/libprotobuf.so', "创建 compat .so 软链接")

# 验证旧库符号
out, _ = run('nm -D /usr/local/lib/compat/libprotobuf.so.19.0.0 2>/dev/null | grep AddDescriptors | head -2')
print(f"  旧库 AddDescriptors 符号: {'存在' if out.strip() else '不存在!'}")

# 备份原始 nfdump 并创建 wrapper
out, _ = run('ls -la /Agent/bin/nfdump 2>/dev/null')
if 'nfdump.real' not in out:
    run('cp /Agent/bin/nfdump /Agent/bin/nfdump.real', "备份 nfdump → nfdump.real")
    print("  已备份 nfdump → nfdump.real")
else:
    print("  nfdump.real 已存在，跳过备份")

# 创建 wrapper 脚本
wrapper = '''#!/bin/bash
# nfdump wrapper - load compat protobuf library
export LD_LIBRARY_PATH=/usr/local/lib/compat:$LD_LIBRARY_PATH
exec /Agent/bin/nfdump.real "$@"
'''

# 写入 wrapper 脚本
stdin, stdout, stderr = c.exec_command('cat > /Agent/bin/nfdump << \'WRAPPEREOF\'' + wrapper + 'WRAPPEREOF')
stdout.read()
run('chmod +x /Agent/bin/nfdump', "设置 wrapper 执行权限")

# 验证 wrapper
out, _ = run('cat /Agent/bin/nfdump', "验证 wrapper 内容")
print(f"  Wrapper 内容:\n{out.strip()}")

# 测试 nfdump wrapper
out, err = run('LD_LIBRARY_PATH= /Agent/bin/nfdump -V 2>&1 || true', "测试 nfdump wrapper")
if 'symbol lookup error' in out.lower() or 'symbol lookup error' in err.lower():
    print("  [!] nfdump 仍有 symbol lookup error!")
    print(f"  输出: {out.strip()[:200]}")
else:
    print(f"  nfdump 测试输出: {out.strip()[:200]}")
    print("  nfdump wrapper 修复成功!")

# ===== 3. 创建 tisrs.conf =====
print("\n" + "=" * 40)
print("[3] 创建 tisrs.conf 威胁情报配置")
print("=" * 40)

tisrs_conf = """# tisrs.conf - Threat Intelligence Service Configuration
# Format: INI key=value pairs
# This file is read by the threatinfo CGI program

# Threat Intelligence API Key (required)
# KEY=your_api_key_here

# Threat Intelligence API Host (required)
# HOST=api.threatintelligence.example.com

# Threat Intelligence API Port (required)
# PORT=8080

# Currently disabled - fill in values to enable
KEY=
HOST=
PORT=
"""

stdin, stdout, stderr = c.exec_command('mkdir -p /Server/etc && cat > /Server/etc/tisrs.conf << \'TISRSEOF\'' + tisrs_conf + 'TISRSEOF')
stdout.read()
out, _ = run('cat /Server/etc/tisrs.conf', "验证 tisrs.conf")
print(f"  tisrs.conf 已创建:\n{out.strip()}")
print("  (KEY/HOST/PORT 为空，需要填入实际值才能启用威胁情报 API)")

# ===== 4. 修复 httpd error_log 权限 =====
print("\n" + "=" * 40)
print("[4] 修复 httpd error_log 权限")
print("=" * 40)

out, _ = run('ls -ld /etc/httpd/logs/', "修复前 logs 目录权限")
print(f"  修复前: {out.strip()}")
run('chmod 755 /etc/httpd/logs/', "修复 logs 目录权限")
run('touch /etc/httpd/logs/error_log', "创建 error_log 文件")
run('chmod 644 /etc/httpd/logs/error_log', "设置 error_log 权限")
out, _ = run('ls -ld /etc/httpd/logs/ && ls -la /etc/httpd/logs/error_log', "修复后权限")
print(f"  修复后: {out.strip()}")

# ===== 5. 修复 config_pusher crontab (添加环境变量) =====
print("\n" + "=" * 40)
print("[5] 检查 config_pusher crontab")
print("=" * 40)

out, _ = run('crontab -l 2>/dev/null', "当前 crontab")
print(f"  当前 crontab:\n{out.strip()}")

# 检查 config_pusher 的 symbol lookup error 是否已修复
out, _ = run('ldd /Server/bin/config_pusher 2>/dev/null | grep protobuf', "config_pusher protobuf 依赖")
print(f"  config_pusher protobuf: {out.strip()}")

# 检查 libcommon.so 是否有 config::Device 符号
out, _ = run('nm -D /lib64/libcommon.so 2>/dev/null | grep -c "Device.*default_type"', "libcommon.so Device 符号数")
print(f"  libcommon.so Device default_type 符号数: {out.strip()}")

# 如果 config_pusher 有 symbol lookup error，检查是否需要 LD_PRELOAD
out, err = run('/Server/bin/config_pusher 2>&1 | head -5', "config_pusher 直接运行测试")
if 'symbol lookup error' in out.lower():
    print("  [!] config_pusher 仍有 symbol lookup error")
    print(f"  错误: {out.strip()[:300]}")
    print("  需要重新编译 config_pusher 或恢复旧版 libcommon.so")
else:
    print(f"  config_pusher 运行正常或有数据库错误")
    print(f"  输出: {out.strip()[:200]}")

c.close()
print("\n" + "=" * 60)
print("修复脚本完成!")
print("=" * 60)
