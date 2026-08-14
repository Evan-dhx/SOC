import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check build system", r"""
echo "=== 1. tsensor Makefile 目标 ==="
grep -E "^all:|^tsensor:|liblyprobe" /root/tsensor/Makefile | head -10
echo ""
echo "=== 2. 检查已有 .o 文件 ==="
ls /root/tsensor/*.o 2>/dev/null | head -20
echo ""
echo "=== 3. 检查 liblyprobe.so 安装情况 ==="
ls -la /usr/local/lib/liblyprobe* 2>/dev/null
echo ""
echo "=== 4. tsensor 二进制 ==="
ls -la /usr/local/bin/tsensor
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
