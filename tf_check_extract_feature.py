import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("检查 extract_feature CGI", r"""
echo "=== 1. /Agent/cmd/ 下是否有 extract_feature ==="
ls -la /Agent/cmd/ | grep -i "extract\|config"
echo ""
echo "=== 2. ly_server.conf 的 ScriptAlias ==="
grep -n "ScriptAlias\|Listen" /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== 3. 测试 10081 extract_feature 是否可访问 ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST "http://127.0.0.1:10081/extract_feature" -d "test" --max-time 5
echo ""
echo "=== 4. t_agent/t_device 表数据 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_agent; SELECT id,name,ip FROM t_device;" 2>&1 | head -20
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
