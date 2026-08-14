import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_updater GET/POST 验证", r"""
echo "=== 1. GET 当前配置（CGI 是否存活） ==="
curl -s "http://127.0.0.1:10081/config_updater" --max-time 10 | grep -A6 "^dev {" | head -10
echo ""
echo "=== 2. 用 pusher 输出作为 POST body ==="
cd /home/Server/bin
./config_pusher d 2>/dev/null > /tmp/pusher_out.txt
wc -l /tmp/pusher_out.txt
curl -s -X POST "http://127.0.0.1:10081/config_updater" --data-binary @/tmp/pusher_out.txt --max-time 10
echo "POST 完成"
echo ""
echo "=== 3. 写入结果 ==="
grep -A11 "^dev {" /Agent/data/config | head -14
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()