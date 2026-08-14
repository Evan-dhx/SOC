import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("topn 源码 + locinfo/ipinfo 依赖", r"""
echo "=== 1. topn.cpp 源码 ==="
ls -la /root/SOC/ly_server_src/server/topn* 2>/dev/null
find /root/SOC -name "topn.cpp" -not -path "*/node_modules/*" 2>/dev/null | head -5
echo ""
echo "=== 2. locinfo 直接运行 ==="
echo 'ip: 8.8.8.8' | timeout 30 /Server/www/d/locinfo 2>&1 | head -c 300
echo "退出码: $?"
echo ""
echo "=== 3. ipinfo.cpp data_file 路径 ==="
sed -n '20,45p' /root/SOC/ly_server_src/server/ipinfo.cpp
echo ""
echo "=== 4. locinfo.cpp 数据文件 ==="
grep -n "fopen\|\.dat\|\.txt\|data_file\|IP" /root/SOC/ly_server_src/server/locinfo.cpp | head -10
echo ""
echo "=== 5. 找 IP 库文件 ==="
find / -name "ipip*" -o -name "*free*.dat" -o -name "ip.dat" 2>/dev/null | grep -v "tf_old\|bazel" | head -10
ls -la /Server/data/ 2>/dev/null | head -10
ls -la /Agent/data/ 2>/dev/null | head -15
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
