import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("综合验证", r"""
cd /Server/www/ui
echo "=== 1. UI 脚本关键函数 ==="
echo -n "openModal: "; grep -c "function openModal" index.html
echo -n "doSave: "; grep -c "function doSave" index.html
echo -n "doTest: "; grep -c "function doTest" index.html
echo -n "获取配置: "; grep -c "threatconf?op=get" index.html
echo ""
echo "=== 2. CGI 与权限 ==="
ls -la /Server/www/d/threatconf
ls -la /Server/etc/
echo ""
echo "=== 3. CGI 接口状态（登录后 get/save/test） ==="
COOKIE=/tmp/ly_cookie_ti.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
echo -n "get: "; curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo -n "save: "; curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=&tic_host=&tic_port=&tisrs_host=&tisrs_port=" -b $COOKIE --max-time 30
echo ""
echo -n "test(未配置): "; curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""
echo -n "无cookie: "; curl -s "http://127.0.0.1/d/threatconf?op=get" --max-time 30
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