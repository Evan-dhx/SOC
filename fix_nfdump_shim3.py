import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:2000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:300]}")
    return out, err

# ===== 1. 检查两个 libcommon.so =====
print("=" * 60)
print("[1] 检查 /Agent/lib/libcommon.so vs /lib64/libcommon.so")
print("=" * 60)

run('ls -la /Agent/lib/libcommon.so /lib64/libcommon.so 2>/dev/null', "文件信息")
run('md5sum /Agent/lib/libcommon.so /lib64/libcommon.so 2>/dev/null', "MD5 比较")

# 检查 /Agent/lib/libcommon.so 的 protobuf 符号
print("\n--- /Agent/lib/libcommon.so 符号 ---")
run('nm -D /Agent/lib/libcommon.so 2>/dev/null | grep "AddDescriptors\\|AddDescriptorsRunner" | head -5', "AddDescriptors 符号")
run('nm -D /Agent/lib/libcommon.so 2>/dev/null | grep "ConfigC1\\|ConfigD1\\|EventC1\\|FeatureRecordC1\\|FeatureResponseC1\\|GenEventResC1" | head -10', "protobuf 生成类符号")

print("\n--- /lib64/libcommon.so 符号 ---")
run('nm -D /lib64/libcommon.so 2>/dev/null | grep "ConfigC1\\|ConfigD1\\|EventC1\\|FeatureRecordC1\\|FeatureResponseC1\\|GenEventResC1" | head -10', "protobuf 生成类符号")

# ===== 2. 测试 nfdump with /Agent/lib LD_LIBRARY_PATH =====
print("\n" + "=" * 60)
print("[2] 测试 nfdump with /Agent/lib + shim")
print("=" * 60)

out, _ = run('LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so LD_LIBRARY_PATH=/Agent/lib /Agent/bin/nfdump -V 2>&1 || true', "nfdump -V (Agent/lib + shim)")
if 'symbol lookup error' in out.lower():
    print(f"  [!] 仍有错误: {out.strip()[:300]}")
else:
    print(f"  nfdump 输出: {out.strip()[:300]}")
    print("  修复成功!")

# ===== 3. 如果成功，测试实际命令 =====
if 'symbol lookup error' not in out.lower():
    print("\n" + "=" * 60)
    print("[3] 测试 nfdump 实际命令")
    print("=" * 60)
    out, _ = run('LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so LD_LIBRARY_PATH=/Agent/lib /Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current -s record -n 5 2>&1 | head -10', "nfdump 实际命令")
    print(f"  输出: {out.strip()[:500]}")
    
    # ===== 4. 创建 nfdump wrapper =====
    print("\n" + "=" * 60)
    print("[4] 创建 nfdump wrapper")
    print("=" * 60)
    
    # 确保 nfdump.real 是原始二进制
    out, _ = run('file /Agent/bin/nfdump.real 2>/dev/null', "检查 nfdump.real")
    if 'ELF' not in out:
        run('cp /Agent/bin/nfdump /Agent/bin/nfdump.real', "备份原始 nfdump")
    
    wrapper = '''#!/bin/bash
# nfdump wrapper - preload AddDescriptors shim + use /Agent/lib
export LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so
export LD_LIBRARY_PATH=/Agent/lib
exec /Agent/bin/nfdump.real "$@"
'''
    
    stdin, stdout, stderr = c.exec_command("cat > /Agent/bin/nfdump << 'WEOF'\n" + wrapper + "WEOF")
    stdout.read()
    run('chmod +x /Agent/bin/nfdump', "设置权限")
    
    out, _ = run('/Agent/bin/nfdump -V 2>&1 || true', "验证 wrapper")
    print(f"  wrapper 测试: {out.strip()[:300]}")
    
    out, _ = run('/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current -s record -n 5 2>&1 | head -10', "wrapper 实际命令")
    print(f"  实际输出: {out.strip()[:500]}")
    
    print("\n  nfdump wrapper 修复成功!")
else:
    print("\n  [!] /Agent/lib 方案也失败")

c.close()
print("\n" + "=" * 60)
print("完成!")
print("=" * 60)
