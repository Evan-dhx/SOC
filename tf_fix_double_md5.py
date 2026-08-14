import paramiko
import sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 计算 md5(md5("admin"))
plain = "admin"
md5_once = hashlib.md5(plain.encode()).hexdigest()
md5_twice = hashlib.md5(md5_once.encode()).hexdigest()
print(f"md5(admin) = {md5_once}")
print(f"md5(md5(admin)) = {md5_twice}")

cmds = [
    ("修复密码为双重 MD5", f"""
echo "=== 1. 当前密码 ==="
mysql -uroot -ppassword123 server -e "SELECT id, name, pass FROM t_user WHERE name='admin';" 2>&1
echo ""
echo "=== 2. 更新密码为双重 md5 ==="
mysql -uroot -ppassword123 server -e "UPDATE t_user SET pass='{md5_twice}' WHERE name='admin';" 2>&1
echo "已更新"
echo ""
echo "=== 3. 验证 ==="
mysql -uroot -ppassword123 server -e "SELECT id, name, pass FROM t_user WHERE name='admin';" 2>&1
echo ""
echo "=== 4. 模拟前端登录（发 md5 一次值） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass={md5_once}" --max-time 30 2>&1
echo ""
echo "=== 5. curl 明文方式现在应该失败 ==="
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