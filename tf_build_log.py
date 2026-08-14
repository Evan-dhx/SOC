import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("actl 完整错误日志", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make actl > /tmp/actl_build.log 2>&1
echo "exit=$?"
grep -n "error\|Error\|In file" /tmp/actl_build.log | head -15
echo "--- 前 30 行 ---"
head -30 /tmp/actl_build.log
"""),
    ("fsd 完整错误日志", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make fsd > /tmp/fsd_build.log 2>&1
echo "exit=$?"
grep -n "error\|Error\|In file" /tmp/fsd_build.log | head -15
echo "--- 前 30 行 ---"
head -30 /tmp/fsd_build.log
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