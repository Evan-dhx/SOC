import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重跑 pusher 验证配置正确下发", r"""
echo "=== 1. pusher 版本确认 ==="
ls -la /home/Server/bin/config_pusher
echo ""
echo "=== 2. 重跑 pusher ==="
/home/Server/bin/config_pusher > /tmp/pusher3.log 2>&1
echo "exit=$?"
echo ""
echo "=== 3. /Agent/data/config 的 dev 内容（应 id=1 + psk） ==="
grep -A9 "^dev {" /Agent/data/config | head -14
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