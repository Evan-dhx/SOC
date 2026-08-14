import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check config/data/model Makefiles", r"""
echo "=== config Makefile ==="
cat /root/SOC/ly_analyser_src/agent/config/Makefile 2>/dev/null | head -40
echo ""
echo "=== data Makefile ==="
cat /root/SOC/ly_analyser_src/agent/data/Makefile 2>/dev/null | head -40
"""),

    ("Check model Makefile and dbctx", r"""
echo "=== model Makefile ==="
cat /root/SOC/ly_analyser_src/agent/model/Makefile 2>/dev/null | head -30
echo ""
echo "=== dbctx files ==="
ls -la /root/SOC/ly_analyser_src/agent/data/dbctx.* 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
