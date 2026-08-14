import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("引用面排查", r"""
echo "=== 1. libcommon.a 是否含 strings.o ==="
ar t /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null | grep -i string
echo ""
echo "=== 2. 服务器哪些代码 include strings.h ==="
grep -rn "common/strings.h" /root/SOC/ly_analyser_src/agent/ 2>/dev/null | grep -v "\.o:" | head -10
echo ""
echo "=== 3. 服务器 common Makefile ==="
cat /root/SOC/ly_analyser_src/common/Makefile 2>/dev/null | head -30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()