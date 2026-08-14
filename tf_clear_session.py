import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("清空 session", r"""
echo "=== t_user_session 表 admin 记录 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user_session WHERE uid=1;" 2>&1
echo ""
echo "=== 清空 admin 的旧 session ==="
mysql -uroot -ppassword123 server -e "DELETE FROM t_user_session WHERE uid=1;" 2>&1
echo "已清空"
echo ""
echo "=== 验证登录（浏览器需无痕/清 cookie 后测试） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" --max-time 30 2>&1
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