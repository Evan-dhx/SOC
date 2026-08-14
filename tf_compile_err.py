import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("actl 完整编译错误", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make actl 2>&1 | grep -E "error|Error" | head -10
echo "---"
"""),
    ("fsd 完整编译错误", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make fsd 2>&1 | grep -E "error|Error" | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()