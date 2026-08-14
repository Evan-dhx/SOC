import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth.cpp check_user_pass + process", r"""
echo "=== 1. process() 160-200 ==="
sed -n '160,200p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 2. check_user_pass 360-460 ==="
sed -n '360,460p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 3. 前端 auth 调用参数 ==="
grep -rn "auth_target\|auth_user\|auth_pass" /Server/www/ui/static/js/*.js 2>/dev/null | head -8
echo ""
echo "=== 4. t_user/t_user_session 表 ==="
mysql -uroot -ppassword123 server -e "SHOW TABLES; SELECT id,username FROM t_user;" 2>&1 | head -20
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
