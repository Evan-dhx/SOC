import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Add mo_req.o to libcommon", r"""
echo "=== 1. 编译 mo_req.o ==="
cd /root/SOC/ly_analyser_src/common
g++ -c -Wall -g -fPIC -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o mo_req.o mo_req.cpp 2>&1 | grep -E "error:" | head -5
echo "Compile exit: $?"
ls -la mo_req.o 2>/dev/null && echo "OK" || echo "FAIL"
echo ""
echo "=== 2. 重新打包 libcommon ==="
rm -f libcommon.a libcommon.so
ar rcs libcommon.a *.o
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -5
echo "Link exit: $?"
echo ""
echo "=== 3. 验证 mo 符号 ==="
nm -D libcommon.so | grep -c "stAddWhere"
echo ""
echo "=== 4. 安装到所有位置 ==="
cp libcommon.so /lib64/
cp libcommon.so /usr/lib64/
cp libcommon.so /Agent/lib/
ldconfig
echo "安装完成"
"""),

    ("Rebuild mo and install all", r"""
echo "=== 5. 重新编译 mo ==="
cd /root/SOC/ly_server_src/server
rm -f mo
make mo 2>&1 | tail -5
echo "Exit: $?"
ls -lh mo 2>/dev/null && echo "OK" || echo "FAIL"
echo ""
echo "=== 6. make install 全部部署 ==="
make install 2>&1 | tail -5
echo ""
echo "=== 7. 验证部署 ==="
ls -la /Server/www/d/mo /Server/bin/config_pusher /Server/bin/gen_event 2>/dev/null | awk '{print $5, $9}'
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
