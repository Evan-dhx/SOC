import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find extractor source", r"""
echo "=== 1. 搜索 extractor 源码 ==="
find /root/SOC/ly_analyser_src -name "*extractor*" -type f 2>/dev/null | head -10
echo ""
echo "=== 2. 搜索 Makefile 引用 extractor ==="
grep -rn "extractor" /root/SOC/ly_analyser_src --include="Makefile" 2>/dev/null | head -10
echo ""
echo "=== 3. extractor 源码文件 ==="
ls -la /root/SOC/ly_analyser_src/agent/ 2>/dev/null
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
