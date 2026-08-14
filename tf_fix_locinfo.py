import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("locinfo 加保护", r"""
cd /root/SOC/ly_server_src/server
python3 - <<'PYEOF'
src = open('locinfo.cpp').read()
open('locinfo.cpp.bak','w').write(src)
old = '''  cgicc::Cgicc cgi;

  init(ipip_file);
'''
new = '''  cgicc::Cgicc cgi;

  struct stat st;
  if (stat(ipip_file, &st) != 0 || st.st_size <= 0) {
    cout << "[]" << endl;
    return;
  }
  init(ipip_file);
'''
if old in src:
    src = src.replace(old, new)
    open('locinfo.cpp','w').write(src)
    print("已添加文件检查")
else:
    print("未找到目标代码段")
PYEOF
echo ""
echo "=== 1. 确认修改 ==="
grep -n -A6 "cgicc::Cgicc cgi;" locinfo.cpp | head -12
echo ""
echo "=== 2. 重编译 locinfo ==="
g++ locinfo.cpp dbc.o -Wall -g -std=c++17 -fpermissive -lpthread -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o locinfo 2>&1 | head -5
echo "编译退出码: $?"
echo ""
echo "=== 3. 直接运行测试（无文件应输出 []） ==="
echo 'iplist: 8.8.8.8' | timeout 30 ./locinfo 2>&1 | head -c 100
echo "退出码: $?"
echo ""
echo "=== 4. 部署 + web 测试 ==="
cp locinfo /Server/www/d/locinfo
chmod 755 /Server/www/d/locinfo
COOKIE=/tmp/ly_cookie_loc.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30 >/dev/null
echo -n "locinfo web: "
curl -s "http://127.0.0.1/d/locinfo?action=get&iplist=8.8.8.8" -b $COOKIE --max-time 60 2>&1 | head -c 100
echo ""
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