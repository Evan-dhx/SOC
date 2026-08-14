import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("前端 index.html + CGI 编译时间清单", r"""
echo "=== 1. /Server/www/ui/index.html 内容 ==="
cat /Server/www/ui/index.html
echo ""
echo "=== 2. 所有 CGI 编译时间 ==="
ls -la /Server/www/d/ | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 3. server Makefile 的 WWW_EXES ==="
grep -n "WWW_EXES\|SRCS\|EXES" /root/SOC/ly_server_src/server/Makefile | head -15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
