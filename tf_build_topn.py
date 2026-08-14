import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译部署 topn", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. topn.cpp 头文件 ==="
head -15 topn.cpp | grep include
echo ""
echo "=== 2. 编译 topn ==="
g++ topn.cpp dbc.o -Wall -g -std=c++17 -fpermissive -lpthread -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o topn 2>&1 | tail -5
ls -la topn 2>/dev/null
echo ""
echo "=== 3. 符号检查 ==="
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r topn 2>&1 | grep -c "undefined" || echo "0"
echo ""
echo "=== 4. 部署 + 测试 ==="
cp topn /Server/www/d/topn
chmod 755 /Server/www/d/topn
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c /tmp/ly_cookie_topn.txt --max-time 30 >/dev/null
echo -n "topn 接口: "
curl -s "http://127.0.0.1/d/topn?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b /tmp/ly_cookie_topn.txt --max-time 90 2>&1 | head -c 300
echo ""
echo ""
echo "=== 5. Makefile 补 topn 目标（供以后使用） ==="
grep -n "topn" Makefile | head -3 || echo "Makefile 无 topn，添加："
echo "SRCS+=topn.cpp" >> /dev/null
sed -i 's|^WWW_EXES+=evidence |WWW_EXES+=evidence \ntopn:topn.cpp dbc.o\n\t$(CXX) $^ $(CXXFLAGS) $(INCS) $(LDFLAGS) $(LIBS) $(LDLIBS) -o $@|' Makefile 2>/dev/null
grep -n -A2 "topn:topn" Makefile | head -4
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
