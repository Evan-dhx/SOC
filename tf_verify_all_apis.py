import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("验证各 web 接口", r"""
echo "=== 1. event 接口 ==="
curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 800
echo ""
echo ""
echo "=== 2. mo 接口 ==="
curl -s "http://127.0.0.1/d/mo?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 800
echo ""
echo ""
echo "=== 3. config 接口 ==="
curl -s "http://127.0.0.1/d/config?action=get" --max-time 30 2>&1 | head -c 500
echo ""
echo ""
echo "=== 4. auth 接口（登录） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "username=admin&password=admin" --max-time 30 2>&1 | head -c 500
echo ""
echo ""
echo "=== 5. 页面主入口 ==="
curl -s -o /dev/null -w "index: HTTP %{http_code}\n" "http://127.0.0.1/" --max-time 30
curl -s -o /dev/null -w "vis: HTTP %{http_code}\n" "http://127.0.0.1/vis" --max-time 30
echo ""
echo "=== 6. feature 其他类型 ==="
for t in dns service ip_scan port_scan; do
  echo -n "$t: "
  curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=$t&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | grep -c "devid"
done
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
