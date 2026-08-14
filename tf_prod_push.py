import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("生产模式 pusher 下发 + 验证全链路", r"""
echo "=== 1. 确认配置已修复（GET） ==="
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null | head -5
echo ""
echo "=== 2. 生产模式跑 config_pusher ==="
/home/Server/bin/config_pusher > /tmp/pusher_prod.log 2>&1
echo "exit=$?"
cat /tmp/pusher_prod.log
echo ""
echo "=== 3. agent 配置中的 dev（应 id=1 + psk） ==="
grep -A15 "^dev {" /Agent/data/config | head -18
echo ""
echo "=== 4. nftls server 状态 ==="
ss -tlnp 2>/dev/null | grep 19996 || echo "19996 未监听"
cat /Agent/etc/nftls.psk 2>/dev/null | sed 's/:.*/:***/'
echo ""
echo "=== 5. 重启 tsensor（使用加密链路） ==="
sed -i 's|^psk=.*|psk=43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa|' /Agent/etc/tsensor.conf
grep "psk=" /Agent/etc/tsensor.conf
systemctl restart tsensor 2>&1
sleep 3
systemctl is-active tsensor
ss -tlnp 2>/dev/null | grep 19996 || echo "TLS 端口未监听"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()