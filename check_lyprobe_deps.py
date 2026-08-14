"""
检查并修复 ly_probe 编译依赖问题
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("检查 ly_probe 编译依赖问题")
print("=" * 60)

cmds = [
    ("检查 .deps 目录", "ls -la /root/ly_probe/.deps/ 2>/dev/null || echo 'NOT FOUND'"),
    ("检查 Makefile 中的 .deps 引用", "grep -n '\\.deps' /root/ly_probe/Makefile | head -20"),
    ("检查 lyprobe_demo 相关配置", "grep -n 'lyprobe_demo' /root/ly_probe/Makefile | head -10"),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8', errors='replace'))

print("\n" + "=" * 60)
print("尝试修复方案...")
print("=" * 60)

# 方案1: 完全清理并重新 configure
fix_cmd = """
cd /root/ly_probe

# 完全清理
rm -rf .deps
make distclean 2>/dev/null || true

# 重新 configure
./configure --prefix=/usr/local 2>&1 | tail -10

# 检查 .deps 是否生成
echo ""
echo "=== configure 后 .deps 目录 ==="
ls -la .deps/ 2>/dev/null || echo "NO .deps"

# 尝试编译
echo ""
echo "=== 开始编译 ==="
make -j2 2>&1 | tail -30
"""

stdin, stdout, stderr = client.exec_command(fix_cmd, timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("STDERR:", err)

client.close()
