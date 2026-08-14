"""
修复 servicePlugin.c 编译错误并重新编译
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("修复 servicePlugin.c 并重新编译")
print("=" * 60)

# 步骤1: 停止服务
print("\n[1] 停止服务...")
stdin, stdout, stderr = client.exec_command("systemctl stop lyprobe.service", timeout=10)
stdout.read()

# 步骤2: 修复 servicePlugin.c
print("[2] 修复 servicePlugin.c...")

# 读取文件
sftp = client.open_sftp()
with sftp.open('/root/ly_probe/plugins/servicePlugin.c', 'r') as f:
    content = f.read().decode('utf-8', errors='replace')

# 添加缺少的头文件
if '#include <dirent.h>' not in content:
    content = content.replace(
        '#include "nprobe.h"',
        '#include "nprobe.h"\n#include <dirent.h>'
    )
    print("  已添加 dirent.h")

# 检查 copyInt64 问题
if 'copyInt64' in content:
    # 查看 nprobe.h 中是否有 copyInt64
    print("  检查 copyInt64...")

# 写回
with sftp.open('/root/ly_probe/plugins/servicePlugin.c', 'w') as f:
    f.write(content)
sftp.close()

# 步骤3: 检查 copyInt64
print("[3] 检查 copyInt64...")
stdin, stdout, stderr = client.exec_command("""
grep -n 'copyInt64' /root/ly_probe/plugins/servicePlugin.c | head -5
grep -rn 'copyInt64' /root/ly_probe/*.h /root/ly_probe/*.c 2>/dev/null | head -5
""", timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 步骤4: 重新编译
print("[4] 重新编译 servicePlugin...")
stdin, stdout, stderr = client.exec_command("""
cd /root/ly_probe/plugins
gcc -shared -fPIC -O2 -DHAVE_CONFIG_H \
    -I.. -I/usr/local/include \
    -o /usr/local/lib/lyprobe/plugins/servicePlugin.so \
    servicePlugin.c cJSON.c -lpcre 2>&1 | tail -20

echo ""
echo "=== 验证 ==="
ls -la /usr/local/lib/lyprobe/plugins/servicePlugin.so
strings /usr/local/lib/lyprobe/plugins/servicePlugin.so | grep 'disabled' || echo "PCRE 已启用!"
""", timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# 步骤5: 启动服务
print("[5] 启动服务...")
for cmd in ["systemctl start lyprobe.service", "sleep 3"]:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.read()

# 步骤6: 验证
print("[6] 验证...")
stdin, stdout, stderr = client.exec_command("""
journalctl -u lyprobe --no-pager -n 15 | grep -E 'plugin|WARNING|enabled'
""", timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
