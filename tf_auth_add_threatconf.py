import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth 白名单加 threatconf + 重编译部署", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. 修改 api_set ==="
python3 - <<'PYEOF'
src = open('auth.cpp').read()
old = '"threatinfopro", "geoinfo", "auth_status", "sctl", "event_feature", "evidence"};'
new = '"threatinfopro", "geoinfo", "auth_status", "sctl", "event_feature", "evidence", "threatconf"};'
if 'threatconf' in src:
    print('已包含 threatconf')
else:
    if old in src:
        src = src.replace(old, new)
        open('auth.cpp', 'w').write(src)
        print('已添加 threatconf 到白名单')
    else:
        print('未找到目标行')
PYEOF
grep -n "threatconf" auth.cpp | head -3
echo ""
echo "=== 2. 重编译 auth ==="
g++ auth.cpp dbc.o -Wall -g -std=c++17 -fpermissive -lpthread -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o auth 2>&1 | head -5
echo "编译退出码: $?"
echo ""
echo "=== 3. 部署 ==="
cp auth /Server/www/d/auth
chmod 755 /Server/www/d/auth
echo "已部署"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()