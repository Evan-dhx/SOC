import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 拉取 threatconf.cpp 源码到本地
sftp = client.open_sftp()
sftp.get('/root/SOC/ly_server_src/server/threatconf.cpp', r'd:\QorderProject\SOC\ly_server\src\server\threatconf.cpp')
# 同时拉取修改后的 auth.cpp
sftp.get('/root/SOC/ly_server_src/server/auth.cpp', r'd:\QorderProject\SOC\ly_server\src\server\auth.cpp')
sftp.close()
print("threatconf.cpp / auth.cpp 已同步到本地源码库")

cmds = [
    ("服务器最终核对", r"""
cd /Server/www/ui
echo "=== 1. 注入块完整性 ==="
for m in ly-tech-v2 ly-net-anim ly-brand-rename ly-force-dark ly-threat-conf ly-ti-btn; do
  echo -n "$m: "; grep -c "$m" index.html
done
echo ""
echo "=== 2. CGI 状态 ==="
ls -la /Server/www/d/threatconf
echo ""
echo "=== 3. 接口存活 ==="
COOKIE=/tmp/ly_cookie_final.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
echo -n "threatconf get: "; curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo(原接口不受影响): "; curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30 | head -c 120
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