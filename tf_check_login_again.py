import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("查当前状态", r"""
echo "=== 1. t_user admin 当前状态 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user WHERE name='admin';" 2>&1
echo ""
echo "=== 2. 当前时间 ==="
date +%s
echo ""
echo "=== 3. 直接登录测试 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" --max-time 30 2>&1
echo ""
echo "=== 4. auth.cpp md5 校验逻辑 ==="
grep -n -A5 "md5\|MD5\|pass" /root/SOC/ly_server_src/server/auth.cpp | head -20
echo ""
echo "=== 5. t_user_session_history 最近失败记录 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user_session_history WHERE uid=1 ORDER BY time DESC LIMIT 5;" 2>&1
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