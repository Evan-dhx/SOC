import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("最终清理与恢复", r"""
echo "=== 1. 确认模拟服务已停止 ==="
echo -n "18090 监听数: "; ss -tlnp 2>/dev/null | grep -c 18090
echo ""
echo "=== 2. 清空威胁情报配置 ==="
COOKIE=/tmp/ly_cookie_clean.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=&tic_host=&tic_port=&tisrs_host=&tisrs_port=" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 3. 验证恢复未配置状态 ==="
echo -n "threatconf get: "; curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 4. 清理临时文件 ==="
rm -f /tmp/sim_ti_server.py /tmp/sim_ti_server.log /tmp/ly_cookie_*.txt
echo "已清理"
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