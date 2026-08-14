import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("process() 和 dbctx", r"""
echo "=== 1. process() 函数体 ==="
sed -n '297,360p' /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp
echo ""
echo "=== 2. dbctx.h 内容 ==="
cat /root/SOC/ly_analyser_src/agent/data/dbctx.h 2>/dev/null | head -60
echo ""
echo "=== 3. data 目录文件 ==="
ls /root/SOC/ly_analyser_src/agent/data/
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
