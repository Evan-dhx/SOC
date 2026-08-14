import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("actl 链接错误", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make actl > /tmp/a.log 2>&1
grep -E "undefined reference|error" /tmp/a.log | head -8
"""),
    ("fsd 编译错误", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make fsd > /tmp/f.log 2>&1
grep -B5 "error:" /tmp/f.log | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()