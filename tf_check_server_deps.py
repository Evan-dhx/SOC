import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check common deps for ly_server", r"""
echo "=== 1. ly_server common 目录 ==="
ls -la /root/SOC/ly_server_src/common/ | head -10
echo ""
echo "=== 2. libcommon.a 时间对比 ==="
stat -c "%y %n" /root/SOC/ly_server_src/common/libcommon.a /root/SOC/ly_analyser_src/common/libcommon.a /lib64/libcommon.so 2>/dev/null
echo ""
echo "=== 3. mysqlclient 库 ==="
ls -la /usr/lib64/libmysqlclient* 2>/dev/null | head -5
ls -la /usr/lib64/libmariadb* 2>/dev/null | head -5
echo ""
echo "=== 4. config_pusher.cpp 头部 include ==="
head -20 /root/SOC/ly_server_src/server/config_pusher.cpp
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
