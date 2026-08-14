import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Build config_updater", r"""
echo "=== 1. 编译 config_updater ==="
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f config_updater config_updater.o
make config_updater 2>&1 | tail -6
echo "Exit: $?"
ls -lh config_updater 2>/dev/null && echo "OK" || echo "FAIL"
"""),

    ("Deploy and configure Apache", r"""
echo "=== 2. 部署 config_updater ==="
cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/config_updater
chmod +x /Agent/cmd/config_updater
echo "部署完成"
echo ""
echo "=== 3. 配置 Apache 监听 10081 ==="
cat >> /etc/httpd/conf.d/ly_server.conf << 'EOF'

# Agent config updater CGI on port 10081
Listen 10081
ScriptAlias /config_updater "/Agent/cmd/config_updater"
<Directory "/Agent/cmd">
    Options +ExecCGI
    AllowOverride None
    Require all granted
    SetHandler cgi-script
</Directory>
EOF
echo "配置已添加"
echo ""
echo "=== 4. 检查配置语法 ==="
httpd -t 2>&1 | head -5
echo ""
echo "=== 5. 重启 httpd ==="
systemctl restart httpd 2>&1 | head -3
sleep 2
ss -tlnp | grep -E "10081|:80 "
echo ""
echo "=== 6. 测试 config_updater CGI ==="
curl -s -X POST -d "test" http://127.0.0.1:10081/config_updater -w "\nHTTP:%{http_code}\n" 2>&1 | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
