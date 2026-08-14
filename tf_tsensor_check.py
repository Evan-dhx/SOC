import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("tsensor 部署调查", r"""
echo "=== 1. tsensor 位置 ==="
which tsensor 2>&1
ls -la $(which tsensor 2>/dev/null) 2>/dev/null
echo ""
echo "=== 2. 运行中的 tsensor 进程 ==="
ps aux | grep tsensor | grep -v grep | head -5
echo ""
echo "=== 3. 依赖库 ==="
ldd $(which tsensor 2>/dev/null) 2>/dev/null | head -12
echo ""
echo "=== 4. 帮助信息 ==="
tsensor --help 2>&1 | head -30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()