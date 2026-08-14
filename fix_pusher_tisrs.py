import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:3000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:500]}")
    return out, err

# =====================================================================
# PART 1: 检查 config_pusher 的 protobuf 符号状态
# =====================================================================
print("=" * 70)
print("PART 1: 检查 config_pusher 的 protobuf 符号")
print("=" * 70)

# 检查 config_pusher 的未定义 protobuf 符号
print("\n--- config_pusher 的 AddDescriptors 符号 ---")
run('nm -D /Server/bin/config_pusher 2>/dev/null | grep "AddDescriptors" | head -5', "AddDescriptors")

print("\n--- config_pusher 的 config:: 未定义符号 ---")
run('nm -D /Server/bin/config_pusher 2>/dev/null | grep " U " | grep "_ZN6config" | head -10', "config:: 未定义符号")

# 检查 config_pusher 是否有那个 Device 符号
print("\n--- config_pusher 的 Device 符号 ---")
run('nm -D /Server/bin/config_pusher 2>/dev/null | grep "Device.*permission\|Device.*default_type" | head -5', "Device 符号")

# 检查 config_pusher 源码位置
print("\n--- config_pusher 源码 ---")
run('ls /root/SOC/ly_server_src/server/config_pusher.cpp 2>/dev/null', "源码")
run('ls /root/SOC/ly_server_src/server/Makefile 2>/dev/null || ls /root/SOC/ly_server_src/Makefile 2>/dev/null || ls /root/SOC/ly_server_src/server/CMakeLists.txt 2>/dev/null', "构建文件")

# =====================================================================
# PART 2: 从 crontab 环境运行 config_pusher
# =====================================================================
print("\n" + "=" * 70)
print("PART 2: 从 crontab 环境运行 config_pusher")
print("=" * 70)

# 清空日志并等待下次 crontab 运行
run('echo "=== TEST RUN $(date) ===" >> /data/log/config_pusher.log', "标记日志")

# 用 cron 的环境运行
print("\n--- 模拟 cron 环境运行 ---")
out, _ = run('env -i HOME=/root PATH=/usr/bin:/bin /Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "cron 环境运行")

# 检查日志是否有新错误
print("\n--- 检查最新日志 ---")
run('tail -5 /data/log/config_pusher.log 2>/dev/null', "最新日志")

# =====================================================================
# PART 3: 修复 tisrs.conf (移除多余行)
# =====================================================================
print("\n" + "=" * 70)
print("PART 3: 修复 tisrs.conf")
print("=" * 70)

tisrs_content = """# Threat Intelligence Service Configuration
# This file is read by the threatinfo CGI program

# Threat Intelligence API Key (required, leave empty to disable)
KEY=

# Threat Intelligence API Host (required)
HOST=

# Threat Intelligence API Port (required)
PORT=
"""

# 写入正确的 tisrs.conf
stdin, stdout, stderr = c.exec_command(f"cat > /Server/etc/tisrs.conf << 'TISRSEOF'\n{tisrs_content}TISRSEOF")
stdout.read()
print("  tisrs.conf 已修复")

# 验证
run('cat /Server/etc/tisrs.conf', "验证 tisrs.conf")

# =====================================================================
# PART 4: 检查 config_pusher 是否需要重新编译
# =====================================================================
print("\n" + "=" * 70)
print("PART 4: 检查 config_pusher 源码和构建")
print("=" * 70)

# 检查 config_pusher 的链接依赖
run('ldd /Server/bin/config_pusher 2>/dev/null | grep -i "protobuf\\|common\\|not found" | head -10', "config_pusher 依赖")

# 检查 Server 源码目录结构
run('ls /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | head -10', "Server 源码")
run('ls /root/SOC/ly_server_src/Makefile /root/SOC/ly_server_src/server/Makefile /root/SOC/ly_server_src/CMakeLists.txt 2>/dev/null', "构建文件")

# 检查 config_pusher 的 .pb.cc 源码版本
print("\n--- Server 的 .pb.cc 文件 ---")
run('find /root/SOC/ly_server_src/ -name "config.pb.cc" 2>/dev/null', "config.pb.cc 位置")
run('grep "AddDescriptors\|AddDescriptorsRunner" /root/SOC/ly_server_src/common/config.pb.cc 2>/dev/null | head -5', "protobuf 版本标记")

# 检查 common_oldabi 目录
run('ls /root/SOC/ly_server_src/common_oldabi/ 2>/dev/null | head -10', "common_oldabi 目录")
run('grep "AddDescriptors\|AddDescriptorsRunner" /root/SOC/ly_server_src/common_oldabi/config.pb.cc 2>/dev/null | head -5', "oldabi protobuf 版本")

# =====================================================================
# PART 5: 重新编译 config_pusher (如果需要)
# =====================================================================
print("\n" + "=" * 70)
print("PART 5: 尝试重新编译 config_pusher")
print("=" * 70)

# 检查是否有 Makefile
out, _ = run('cat /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -30', "Server Makefile 头部")
out2, _ = run('grep -n "config_pusher" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -10', "config_pusher 构建规则")

# 尝试编译
if out2.strip():
    print("\n--- 尝试 make config_pusher ---")
    out, err = run('cd /root/SOC/ly_server_src/server && make config_pusher 2>&1 | tail -20', "make config_pusher", timeout=120)
    
    # 检查是否生成了新的 config_pusher
    run('ls -la /root/SOC/ly_server_src/server/config_pusher 2>/dev/null', "编译结果")
    
    # 测试
    out, _ = run('/root/SOC/ly_server_src/server/config_pusher 2>&1; echo "EXIT=$?"', "测试重新编译 config_pusher")
    if 'EXIT=0' in out and 'symbol lookup error' not in out.lower():
        print("  重新编译 config_pusher 成功!")
        # 部署
        run('cp /root/SOC/ly_server_src/server/config_pusher /Server/bin/config_pusher', "部署 config_pusher")
        run('chmod +x /Server/bin/config_pusher', "设置权限")
        out2, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "验证部署")
        print(f"  部署验证: {out2.strip()[:200]}")
    else:
        print(f"  编译或测试失败: {out.strip()[:500]}")
else:
    print("  未找到 config_pusher 的构建规则")
    # 检查是否有其他构建方式
    run('find /root/SOC/ly_server_src/ -name "Makefile" -exec grep -l "config_pusher" {} \\; 2>/dev/null', "搜索包含 config_pusher 的 Makefile")
    run('find /root/SOC/ly_server_src/ -name "*.cmake" -o -name "CMakeLists.txt" 2>/dev/null | head -5', "搜索 CMake 文件")

c.close()
print("\n" + "=" * 70)
print("修复完成!")
print("=" * 70)
