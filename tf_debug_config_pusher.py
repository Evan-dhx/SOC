import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Run config_pusher debug", r"""
echo "=== 1. debug 模式运行（完整输出） ==="
cd /Server/bin
timeout 60 ./config_pusher d 2>&1 | head -50
echo ""
echo "=== 2. t_config 表检查 ==="
mysql -e "SHOW TABLES FROM server LIKE 't_config';" 2>/dev/null
mysql -e "SELECT * FROM server.t_config LIMIT 5;" 2>/dev/null
echo ""
echo "=== 3. auth 时间戳 ==="
stat -c "%y %n" /Server/www/d/auth /root/SOC/ly_server_src/server/auth
echo ""
echo "=== 4. config_updater 日志（journal） ==="
journalctl --no-pager --since '5 minutes ago' 2>/dev/null | grep -iE "config_updater|Successfully updated|Updating config" | tail -5
echo ""
echo "=== 5. httpd 访问日志（config_updater 请求） ==="
tail -10 /var/log/httpd/ly_access_log 2>/dev/null | grep config_updater
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
