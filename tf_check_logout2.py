import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("logout 脚本 + extract_event 400 逻辑", r"""
echo "=== 1. logout 脚本内容 ==="
cat /Server/www/d/logout
echo ""
echo "=== 2. extract_event.cpp 400 来源 ==="
grep -n "400\|Invalid\|LoadFromString\|ParseFromString" /root/SOC/ly_analyser_src/agent/handlers/extract_event.cpp | head -10
echo ""
echo "=== 3. extract_event.cpp 主流程 ==="
sed -n '/int main/,+25p' /root/SOC/ly_analyser_src/agent/handlers/extract_event.cpp
echo ""
echo "=== 4. event.cpp 如何调 extract_event ==="
grep -n -B3 -A10 "extract_event" /root/SOC/ly_server_src/server/event.cpp | head -30
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
