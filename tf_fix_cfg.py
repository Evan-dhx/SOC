import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("修复配置 + 验证 config_updater 链路", r"""
echo "=== 1. 恢复最小合法配置 ==="
cat > /Agent/data/config <<'EOF'
controller {
  host: "127.0.0.1"
  port: "10081"
}
EOF
echo "写入完成"
echo ""
echo "=== 2. GET 验证（应返回最小配置） ==="
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>&1 | head -10
echo ""
echo "=== 3. POST 全量配置（用 pusher 输出） ==="
cd /home/Server/bin
./config_pusher d 2>/dev/null > /tmp/pusher_body2.txt
echo "pusher 输出行数: $(wc -l < /tmp/pusher_body2.txt)"
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST CONTENT_LENGTH=$(wc -c < /tmp/pusher_body2.txt) /home/Agent/cmd/config_updater < /tmp/pusher_body2.txt 2>&1
echo "exit=$?"
echo ""
echo "=== 4. 验证写入结果 ==="
grep -A12 "^dev {" /Agent/data/config | head -15
echo ""
echo "=== 5. 验证 psk 字段 ==="
grep "psk:" /Agent/data/config
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