import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("改 DocumentRoot + 测试 CGI", r"""
echo "=== 1. 修改 DocumentRoot ==="
sed -i 's|DocumentRoot "/Server/www"|DocumentRoot "/Server/www/ui"|; s|<Directory "/Server/www">|<Directory "/Server/www/ui">|' /etc/httpd/conf.d/ly_server.conf
apachectl configtest 2>&1
systemctl restart httpd
sleep 1
echo ""
echo "=== 2. 验证 / 和 /ui/ ==="
curl -s -o /dev/null -w "/: HTTP %{http_code}\n" "http://127.0.0.1/" --max-time 15
curl -s -o /dev/null -w "/ui/: HTTP %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
curl -s -o /dev/null -w "/static/js/: HTTP %{http_code}\n" "http://127.0.0.1/static/js/main.ff156c89.chunk.js" --max-time 15
echo ""
echo "=== 3. 测试 event/sctl/mo 接口 ==="
curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 300
echo ""
curl -s "http://127.0.0.1/d/sctl?action=get" --max-time 30 2>&1 | head -c 300
echo ""
curl -s "http://127.0.0.1/d/mo?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 300
echo ""
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
