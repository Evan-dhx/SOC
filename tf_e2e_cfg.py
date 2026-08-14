import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("端到端配置链路：API 设置 psk → 下发 → nftls/tsensor 切换", r"""
set -e
COOKIE=/tmp/ly_cookie_tls.txt
rm -f $COOKIE
echo "===== 1. 登录流影 ====="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
echo "登录 OK"
echo ""
echo "===== 2. 当前设备列表（含 tls 字段） ====="
curl -s -X POST "http://127.0.0.1/d/config" -d "op=get&type=agent&target=device" -b $COOKIE --max-time 10 | python3 -m json.tool 2>/dev/null | head -30
echo ""
echo "===== 3. 生成 PSK 并设置到设备 1 ====="
PSK=$(openssl rand -hex 24)
echo "PSK=$PSK"
curl -s -X POST "http://127.0.0.1/d/config" -d "op=mod&type=agent&target=device&id=1&name=默认设备&psk=$PSK" -b $COOKIE --max-time 10
echo ""
echo "===== 4. 数据库确认 ====="
mysql -uroot -ppassword123 server -e "SELECT id,name,tls_psk FROM t_device WHERE id=1;" 2>/dev/null
echo ""
echo "===== 5. config_pusher 下发 ====="
/home/Server/bin/config_pusher > /tmp/pusher.log 2>&1 || echo "pusher 退出码 $?"
echo "agent 配置中的 psk:"
grep -A5 "dev {" /Agent/data/config | head -8
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