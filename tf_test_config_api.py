import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config 接口测试 + 插件符号检查", r"""
echo "=== 1. config 各类型测试 ==="
for t in event mo user agent device bwlist internalip; do
  echo -n "type=$t: "
  curl -s "http://127.0.0.1/d/config?type=$t&op=get" --max-time 60 2>&1 | head -c 200
  echo ""
done
echo ""
echo "=== 2. ly_error_log 最新 ==="
tail -6 /var/log/httpd/ly_error_log 2>/dev/null | grep -iE "config|symbol" | head -5
echo ""
echo "=== 3. config_event.so 未定义符号 ==="
nm -u /Server/lib/config_event.so 2>/dev/null | grep -iE "feature|event|config" | head -10
echo ""
echo "=== 4. lib/Makefile ==="
cat /root/SOC/ly_server_src/lib/Makefile | head -50
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
