import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check topn_req.o status", r"""
echo "=== Check topn_req.o ==="
ls -la /root/SOC/ly_analyser_src/common/topn_req.o 2>/dev/null || echo "topn_req.o MISSING"
"""),

    ("Compile topn_req.cpp and repackage libcommon", r"""
echo "=== Compile topn_req.cpp ==="
cd /root/SOC/ly_analyser_src/common

# Compile topn_req.cpp with proper includes
g++ -c -Wall -g -fPIC -std=c++17 -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o topn_req.o topn_req.cpp 2>&1 | grep -E "error:" | head -10
echo "Compile exit: $?"
ls -la topn_req.o 2>/dev/null && echo "OK: topn_req.o generated" || echo "FAIL: topn_req.o not generated"

# Repackage libcommon
rm -f libcommon.a libcommon.so
ar rcs libcommon.a *.o
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lprotobuf -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -5

echo ""
echo "=== Verify symbol ==="
nm libcommon.a 2>/dev/null | grep -i "ComposeReqFilter" | head -3
echo ""
echo "=== Object count ==="
ar t libcommon.a | wc -l
"""),

    ("Install new libcommon.so", r"""
echo "=== Install libcommon.so ==="
cd /root/SOC/ly_analyser_src/common
cp libcommon.so /lib64/
cp libcommon.so /usr/lib64/
ldconfig
echo "Installed at $(date)"
stat -c "%y %n" /lib64/libcommon.so
"""),

    ("Rebuild indexer", r"""
echo "=== Rebuild indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -30
echo ""
echo "Exit code: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer generated" || echo "FAIL: indexer not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err[:2000]}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
