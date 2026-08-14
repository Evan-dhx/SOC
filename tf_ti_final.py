import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("最终状态确认", r"""
echo "=== 1. 清理测试文件 ==="
rm -f /tmp/test_ti.pfx /tmp/test_ti.key /tmp/test_ti.crt
echo "已清理"
echo ""
echo "=== 2. 服务与端口 ==="
systemctl is-active ti-server
ss -tlnp 2>/dev/null | grep -E "8090|8091" | awk '{print $4}'
echo ""
echo "=== 3. MySQL 数据确认 ==="
mysql -uroot -ppassword123 ti_server -e "SELECT COUNT(*) AS ioc总数 FROM t_ioc; SELECT k,v FROM t_config WHERE k LIKE 'https%' OR k='service_key';" 2>/dev/null
echo ""
echo "=== 4. HTTPS 管理界面 + HTTP 查询端口 ==="
curl -sk -o /dev/null -w "https://8090 管理界面: %{http_code}\n" "https://127.0.0.1:8090/" --max-time 5
curl -s -o /dev/null -w "http://8091 查询端口: %{http_code}\n" "http://127.0.0.1:8091/query" --max-time 5
echo ""
echo "=== 5. 流影对接配置 ==="
cat /Server/etc/tisrs.conf | grep -v "^#\|^$"
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