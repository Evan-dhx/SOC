import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("添加 extract_* ScriptAlias", r"""
echo "=== 1. 备份 ly_server.conf ==="
cp /etc/httpd/conf.d/ly_server.conf /etc/httpd/conf.d/ly_server.conf.bak_extract
echo "备份完成"
echo ""
echo "=== 2. 检查是否已有 extract 别名 ==="
grep -n "extract" /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== 3. 追加 ScriptAlias ==="
cat >> /etc/httpd/conf.d/ly_server.conf <<'EOF'

# Agent extract CGIs on port 10081
ScriptAlias /extract_feature "/Agent/cmd/extract_feature"
ScriptAlias /extract_event "/Agent/cmd/extract_event"
ScriptAlias /extract_event_feature "/Agent/cmd/extract_event_feature"
ScriptAlias /extract_pcap "/Agent/cmd/extract_pcap"
EOF
echo "追加完成"
echo ""
echo "=== 4. 检查语法并重启 httpd ==="
apachectl configtest 2>&1
systemctl restart httpd
sleep 2
echo ""
echo "=== 5. 测试 extract_feature 可达性 ==="
curl -s -o /dev/null -w "extract_feature: HTTP %{http_code}\n" -X POST "http://127.0.0.1:10081/extract_feature" -d "devid: 1" --max-time 30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
