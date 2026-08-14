import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重新编译 actl + fsd", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f actl.o fsd.o actl fsd
make actl 2>&1 | tail -3
echo "=== actl 结果 ==="
ls -la actl 2>/dev/null
make fsd 2>&1 | tail -3
echo "=== fsd 结果 ==="
ls -la fsd 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1200]}")

client.close()