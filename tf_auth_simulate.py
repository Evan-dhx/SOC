import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("模拟 Apache 环境测 auth", r"""
echo "=== 1. 带 SCRIPT_NAME 测试（完整 Apache 环境模拟） ==="
echo "auth_user=admin&auth_pass=admin&auth_target=login" | REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST SCRIPT_NAME=/d/auth CONTENT_TYPE=application/x-www-form-urlencoded CONTENT_LENGTH=48 timeout 30 /Server/www/d/auth 2>&1 | head -c 800
echo ""
echo "退出码: $?"
echo ""
echo "=== 2. 只带 SCRIPT_NAME 不带 REMOTE_ADDR ==="
echo "" | SCRIPT_NAME=/d/auth timeout 30 /Server/www/d/auth 2>&1 | head -c 500
echo ""
echo "退出码: $?"
echo ""
echo "=== 3. 不带任何 env（验证 getenv NULL） ==="
echo "" | timeout 30 /Server/www/d/auth 2>&1 | head -c 500
echo ""
echo "退出码: $?"
echo ""
echo "=== 4. check_user_pass 逻辑（300-360 行） ==="
sed -n '300,360p' /root/SOC/ly_server_src/server/auth.cpp
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
