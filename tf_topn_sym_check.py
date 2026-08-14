import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("topn 调用符号确认", r"""
echo "=== 1. topn.cpp 中 getMoIDs 调用 ==="
grep -n "getMoID" /root/SOC/ly_server_src/server/topn.cpp | head -5
echo ""
echo "=== 2. topn.o 未定义符号 ==="
g++ -c -Wall -g -std=c++17 -fpermissive -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -o /tmp/topn_test.o topn.cpp 2>&1 | tail -3
nm -u /tmp/topn_test.o | grep -i "getmo" 
echo ""
echo "=== 3. mo_req.h 声明 ==="
grep -n "getMoID" /root/SOC/ly_analyser_src/common/mo_req.h
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
