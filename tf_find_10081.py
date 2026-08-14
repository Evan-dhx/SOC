import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find 10081 service config", r"""
echo "=== 1. httpd 配置中 10081 ==="
grep -rn "10081" /etc/httpd/ /etc/apache2/ 2>/dev/null | head -10
echo ""
echo "=== 2. httpd 虚拟主机/监听 ==="
cat /etc/httpd/conf/httpd.conf 2>/dev/null | grep -E "^Listen|ServerName" | head -10
ls /etc/httpd/conf.d/ 2>/dev/null
echo ""
echo "=== 3. 查找所有 httpd 相关配置 ==="
find /etc -name "*.conf" 2>/dev/null | xargs grep -l "10081" 2>/dev/null | head -5
echo ""
echo "=== 4. 查找 cgicc/cgi 配置 ==="
grep -rn "ScriptAlias\|AddHandler.*cgi\|Script" /etc/httpd/conf/httpd.conf 2>/dev/null | head -10
echo ""
echo "=== 5. httpd 进程完整命令行 ==="
ps aux | grep "[h]ttpd" | head -3
echo ""
echo "=== 6. 查找 /Server/www 或 CGI 目录 ==="
ls /Server/www/ 2>/dev/null | head -10
ls /Agent/www/ 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
