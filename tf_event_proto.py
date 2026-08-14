import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("event.proto + event.cpp 调用", r"""
echo "=== 1. event.proto EventReq ==="
grep -n -A30 "message EventReq" /root/SOC/ly_analyser_src/common/event.proto | head -40
echo ""
echo "=== 2. event.cpp 中 http_post/url ==="
grep -n "http_post\|10081\|extract\|url" /root/SOC/ly_server_src/server/event.cpp | head -10
echo ""
echo "=== 3. event.cpp process 主流程 ==="
grep -n "static void process\|GetDevs\|PrintToString" /root/SOC/ly_server_src/server/event.cpp | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
