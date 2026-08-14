import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("密码校验 + session 冲突检查", r"""
echo "=== 1. check_user_pass 完整 ==="
sed -n '208,240p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 2. code 码定义 ==="
grep -n "CODE_FAIL_AUTH\|CODE_SUCCEED\|CODE_FAIL_RETRY\|CODE_FAIL_LOGGED\|301\|302\|303\|304" /root/SOC/ly_server_src/server/auth.cpp | head -20
echo ""
echo "=== 3. 当前 admin 的 session 状态 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user_session WHERE uid=1 ORDER BY time DESC LIMIT 3;" 2>&1
echo ""
echo "=== 4. 用新 session（无 cookie）重复登录测试 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -H "Cookie: " --max-time 30 2>&1
echo ""
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -H "Cookie: SESSION_ID=" --max-time 30 2>&1
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