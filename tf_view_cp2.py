import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View config_pusher output logic", r"""
echo "=== 输出/写文件逻辑 ==="
grep -n "WriteToFile\|SerializeToString\|ofstream\|fopen\|/Agent\|/Server\|AGENT\|push\|url\|http" /root/SOC/ly_server_src/server/config_pusher.cpp | head -20
echo ""
echo "=== main 函数 ==="
grep -n -A40 "int main" /root/SOC/ly_server_src/server/config_pusher.cpp | head -60
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
