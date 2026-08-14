import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("topn/locinfo/ipinfo 诊断", r"""
echo "=== 1. ly_error_log 最新 10 行 ==="
tail -10 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 2. topn/locinfo 直接运行 ==="
echo 'devid: 1' | timeout 30 /Server/www/d/topn 2>&1 | head -c 300
echo "退出码: $?"
echo ""
echo "=== 3. topn/locinfo 编译时间 + 符号 ==="
ls -la /Server/www/d/topn /Server/www/d/locinfo 2>/dev/null | awk '{print $6, $7, $8, $9}'
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/www/d/topn 2>&1 | grep -c "undefined"
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/www/d/locinfo 2>&1 | grep -c "undefined"
echo ""
echo "=== 4. ipinfo open error 原因 ==="
grep -n "open error" /root/SOC/ly_server_src/server/ipinfo.cpp | head -3
grep -n "ipip\|IP_LIB\|\.dat\|open(" /root/SOC/ly_server_src/server/ipinfo.cpp | head -10
echo ""
echo "=== 5. IP 库文件位置 ==="
find /Agent /Server /usr/local -name "*.dat" -o -name "ipip*" -o -name "*.ipdb" 2>/dev/null | grep -iv "mysql\|maria" | head -10
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
