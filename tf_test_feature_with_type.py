import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("带 type 参数测试 web feature 接口", r"""
echo "=== 1. type=tcpinit ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786601400" --max-time 90 2>&1 | head -c 3000
echo ""
echo ""
echo "=== 2. type=dns ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=dns&starttime=1786596300&endtime=1786601400" --max-time 90 2>&1 | head -c 3000
echo ""
echo ""
echo "=== 3. 直接调 extract_feature（type=tcpinit） ==="
echo 'devid: 1
type: TCPINIT
starttime: 1786596300
endtime: 1786601400' | timeout 90 /Agent/cmd/extract_feature 2>&1 | head -c 2000
echo ""
echo ""
echo "=== 4. httpd error log ==="
tail -5 /var/log/httpd/error_log 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
