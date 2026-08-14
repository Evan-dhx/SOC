import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重编译 mo_req + 重打包 libcommon", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. mo_req.o vs mo_req.cpp 时间 ==="
ls -la mo_req.o mo_req.cpp 2>/dev/null | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 2. 重新编译 mo_req.o ==="
g++ -c -Wall -g -fPIC -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o mo_req.o mo_req.cpp 2>&1 | tail -3
echo "编译完成"
echo ""
echo "=== 3. 重新打包 libcommon.a ==="
ar rcs libcommon.a mo_req.o
nm libcommon.a | grep "getMoIDs" | head -2
echo ""
echo "=== 4. 重新打包 libcommon.so ==="
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive 2>&1 | tail -3
nm -D libcommon.so | grep "getMoIDs" | head -2
echo ""
echo "=== 5. 同步部署 ==="
cp libcommon.so /lib64/libcommon.so
cp libcommon.so /usr/lib64/libcommon.so
cp libcommon.so /Agent/lib/libcommon.so
cp libcommon.so /home/Agent/lib/libcommon.so
cp libcommon.so /home/Server/lib/libcommon.so
cp libcommon.so /root/SOC/ly_server_src/common/libcommon.so
echo "同步完成"
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
