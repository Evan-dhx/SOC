import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch and build config_pusher", r"""
echo "=== 1. 修改 config_pusher.cpp include 指向新 common ==="
cd /root/SOC/ly_server_src/server
cp config_pusher.cpp config_pusher.cpp.bak_oldinc
sed -i 's|#include "../common/|#include "../../ly_analyser_src/common/|' config_pusher.cpp
head -6 config_pusher.cpp
echo ""
echo "=== 2. 修改 Makefile ==="
cp Makefile Makefile.bak_old
sed -i 's/-std=c++11 -lpthread/-std=c++17 -fpermissive -lpthread/' Makefile
sed -i 's|INCS=-I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I.|INCS=-I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common|' Makefile
grep -E "CXXFLAGS=|INCS=" Makefile | head -2
echo ""
echo "=== 3. 编译 config_pusher ==="
rm -f config_pusher dbc.o config_pusher.o
make config_pusher 2>&1 | tail -10
echo "Exit: $?"
ls -lh config_pusher 2>/dev/null && echo "OK" || echo "FAIL"
"""),

    ("Deploy and test", r"""
echo "=== 4. 部署 ==="
cp /usr/local/bin/config_pusher /usr/local/bin/config_pusher.bak_old 2>/dev/null
cp /root/SOC/ly_server_src/server/config_pusher /Server/bin/config_pusher
chmod +x /Server/bin/config_pusher
echo "部署完成"
echo ""
echo "=== 5. 测试运行 ==="
cd /Server/bin
timeout 60 ./config_pusher 2>&1 | head -20
echo "Exit: $?"
echo ""
echo "=== 6. 检查 config 文件生成 ==="
ls -la /Agent/data/config 2>/dev/null && echo "config 已生成！" || echo "config 未生成"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
