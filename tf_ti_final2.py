import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("最终状态", r"""
echo "=== 1. 服务 ==="
systemctl is-active ti-server
echo ""
echo "=== 2. 管理界面客户端页签 ==="
curl -sk "https://127.0.0.1:8090/" --max-time 5 | grep -o "客户端管理\|client-tbody" | sort -u
echo ""
echo "=== 3. MySQL 客户端数据 ==="
mysql -uroot -ppassword123 ti_server -e "SELECT id,name,order_no,enabled,allowed_ips,update_window,last_update FROM t_client;" 2>/dev/null
echo ""
echo "=== 4. 流影对接（客户A key） ==="
COOKIE=/tmp/ly_cookie_fin.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30 | head -c 80
echo ""
echo -n "测试按钮: "; curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()