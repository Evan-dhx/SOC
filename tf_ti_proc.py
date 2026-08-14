import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("进程与服务文件核查", r"""
echo "=== 1. 8090 进程命令行 ==="
ps -p $(ss -tlnp 2>/dev/null | grep 8090 | grep -oP 'pid=\K[0-9]+' | head -1) -o pid,ppid,cmd 2>/dev/null
echo ""
echo "=== 2. systemd 服务文件 ==="
ls -la /etc/systemd/system/ti-server.service 2>&1
cat /etc/systemd/system/ti-server.service 2>/dev/null | head -10
echo ""
echo "=== 3. 父进程 ==="
PPID_VAL=$(ps -p $(ss -tlnp 2>/dev/null | grep 8090 | grep -oP 'pid=\K[0-9]+' | head -1) -o ppid= 2>/dev/null | tr -d ' ')
ps -p $PPID_VAL -o pid,cmd 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()