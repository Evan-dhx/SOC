import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View config.proto schema", r"""
echo "=== config.proto 关键消息 ==="
grep -n "message\|repeated\|optional\|required" /root/SOC/ly_analyser_src/common/config.proto | head -40
"""),

    ("Check permissions and test POST", r"""
echo "=== 目录权限 ==="
ls -ld /Agent/data /Agent/data/config 2>/dev/null
echo ""
echo "=== 修复权限 ==="
chmod 777 /Agent/data
chown apache:apache /Agent/data 2>/dev/null || true
echo "done"
echo ""
echo "=== 测试有效 POST（最小配置） ==="
curl -s -X POST -d 'dev { id: 1 disabled: false flowtype: "netflow" }' http://127.0.0.1:10081/config_updater -w "\nHTTP:%{http_code}\n"
echo ""
echo "=== 检查 config 文件 ==="
ls -la /Agent/data/config 2>/dev/null && echo "✅ 生成！" || echo "❌ 未生成"
echo ""
echo "=== httpd 错误日志 ==="
tail -3 /var/log/httpd/ly_error_log 2>/dev/null
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
