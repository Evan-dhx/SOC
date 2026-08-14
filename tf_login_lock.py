import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("查锁原因", r"""
echo "=== 1. t_user 表 admin 记录 ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_user WHERE name='admin';" 2>&1
echo ""
echo "=== 2. t_user 表全部字段结构 ==="
mysql -uroot -ppassword123 server -e "DESC t_user;" 2>&1
echo ""
echo "=== 3. auth.cpp 登录逻辑中锁定相关代码 ==="
grep -n "lock\|disable\|fail\|LOCK\|DISABLE" /root/SOC/ly_server_src/server/auth.cpp | head -20
echo ""
echo "=== 4. 直接登录测试（看返回内容） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" --max-time 30 2>&1
echo ""
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -v --max-time 30 2>&1 | tail -5
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