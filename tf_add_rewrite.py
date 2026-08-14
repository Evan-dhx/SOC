import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("配置 auth RewriteRule", r"""
echo "=== 1. SERVER_WWW_DIR 定义 ==="
grep -rn "SERVER_WWW_DIR" /root/SOC/ly_server_src/server/define.h /root/SOC/ly_server_src/common/*.h 2>/dev/null | head -3
echo ""
echo "=== 2. mod_rewrite 是否加载 ==="
httpd -M 2>/dev/null | grep rewrite
echo ""
echo "=== 3. 添加 RewriteRule 到 /d/ Directory ==="
cp /etc/httpd/conf.d/ly_server.conf /etc/httpd/conf.d/ly_server.conf.bak_rewrite
python3 - <<'PYEOF'
import re
conf = open('/etc/httpd/conf.d/ly_server.conf').read()
old = '''<Directory "/Server/www/d">
    Options +ExecCGI
    AllowOverride None
    Require all granted
    AddHandler cgi-script .cgi .pl
    SetHandler cgi-script
</Directory>'''
new = '''<Directory "/Server/www/d">
    Options +ExecCGI
    AllowOverride None
    Require all granted
    AddHandler cgi-script .cgi .pl
    SetHandler cgi-script
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !auth$
    RewriteRule ^(.*)$ auth?auth_target=$1 [QSA,PT,L]
</Directory>'''
if old in conf:
    conf = conf.replace(old, new)
    open('/etc/httpd/conf.d/ly_server.conf','w').write(conf)
    print("RewriteRule 已添加")
else:
    print("未找到目标配置块，当前内容：")
    print(conf)
PYEOF
echo ""
echo "=== 4. 语法检查 + 重启 ==="
apachectl configtest 2>&1
systemctl restart httpd
sleep 1
echo ""
echo "=== 5. 测试：无 cookie 访问 feature（应被 auth 拦截） ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 200
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
