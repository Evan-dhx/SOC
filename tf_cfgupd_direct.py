import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_updater CGI 通路排查", r"""
echo "=== 1. httpd 10081 配置 ==="
grep -rn "10081\|config_updater\|ScriptAlias" /etc/httpd/ /etc/apache/ 2>/dev/null | head -10
echo ""
echo "=== 2. 直接跑 config_updater（模拟 CGI） ==="
cd /home/Agent/cmd
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET ./config_updater 2>&1 | head -15
echo ""
echo "=== 3. POST 直接测试 ==="
cd /home/Server/bin
./config_pusher d 2>/dev/null > /tmp/pusher_body.txt
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST CONTENT_LENGTH=$(wc -c < /tmp/pusher_body.txt) ./config_updater < /tmp/pusher_body.txt 2>&1
echo "exit=$?"
echo ""
echo "=== 4. /Agent/data/config 最新内容（dev 段） ==="
grep -A10 "^dev {" /Agent/data/config 2>/dev/null | head -12
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()