import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View ly_server.conf", r"""
echo "=== ly_server.conf 完整 ==="
cat /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== /Server/www/d 和 ui ==="
ls -la /Server/www/d/ 2>/dev/null | head -15
ls -la /Server/www/ui/ 2>/dev/null | head -15
echo ""
echo "=== 查找 config_updater 的 CGI 入口 ==="
find / -name "config_updater" -type f 2>/dev/null | grep -v proc | head -5
ls -la /var/www/cgi-bin/ 2>/dev/null | head -15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
