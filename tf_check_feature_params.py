import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check feature_req params", r"""
echo "=== 1. feature_req.cpp 参数解析 ==="
grep -n "starttime\|endtime\|start_time\|end_time\|action\|devid\|get\b" /root/SOC/ly_analyser_src/common/feature_req.cpp | head -25
echo ""
echo "=== 2. feature.cpp 查询逻辑 ==="
grep -n -B2 -A15 "op_gget\|op_gget(" /root/SOC/ly_server_src/server/feature.cpp | head -40
echo ""
echo "=== 3. db 文件命名 ==="
ls -la /Agent/data/db/20260813/
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
