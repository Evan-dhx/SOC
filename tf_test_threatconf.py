import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("权限 + threatconf 全链路测试", r"""
echo "=== 1. 调整 /Server/etc 权限（apache 可写） ==="
chown -R apache:apache /Server/etc
ls -la /Server/etc/
echo ""
echo "=== 2. 登录 ==="
COOKIE=/tmp/ly_cookie_tconf.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30
echo ""
echo ""
echo "=== 3. GET 读取（当前应为空配置） ==="
curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 4. POST 保存测试值 ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=test_api_key_123&key=test_key_456&tic_host=10.0.0.1&tic_port=443&tisrs_host=10.0.0.2&tisrs_port=8080" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 5. GET 验证已保存 ==="
curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 6. conf 文件内容 ==="
cat /Server/etc/tic.conf
echo "---"
cat /Server/etc/tisrs.conf
echo ""
echo "=== 7. 测试连通（应返回连接失败/服务返回错误） ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 8. 清理测试值（恢复为空配置） ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=&tic_host=&tic_port=&tisrs_host=&tisrs_port=" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 9. 无 cookie 访问（应 300 未登录） ==="
curl -s "http://127.0.0.1/d/threatconf?op=get" --max-time 30
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