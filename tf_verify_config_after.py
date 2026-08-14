import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config/mo 接口验证", r"""
echo "=== 1. config 各类型 ==="
for t in event mo user agent bwlist internalip; do
  echo -n "type=$t: "
  curl -s "http://127.0.0.1/d/config?type=$t&op=get" --max-time 60 2>&1 | head -c 300
  echo ""
done
echo ""
echo "=== 2. mo 接口（追踪策略） ==="
curl -s "http://127.0.0.1/d/mo?op=get&devid=1" --max-time 60 2>&1 | head -c 1500
echo ""
echo ""
echo "=== 3. mo 分组 ==="
curl -s "http://127.0.0.1/d/mo?op=gget&devid=1" --max-time 60 2>&1 | head -c 500
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
