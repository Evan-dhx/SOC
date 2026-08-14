import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("解锁 + 查锁原因", r"""
echo "=== 1. 解锁 admin ==="
mysql -uroot -ppassword123 server -e "UPDATE t_user SET lockedtime=0 WHERE name='admin';" 2>&1
echo "已解锁"
echo ""
echo "=== 2. 验证登录 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" --max-time 30 2>&1
echo ""
echo ""
echo "=== 3. auth.cpp 锁定触发条件 ==="
sed -n '175,215p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 4. t_user_session 表 admin 相关 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user_session WHERE name='admin';" 2>&1
echo ""
echo "=== 5. 登录失败计数相关代码 ==="
sed -n '250,290p' /root/SOC/ly_server_src/server/auth.cpp
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