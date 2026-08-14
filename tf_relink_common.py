import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View launch scripts", r"""
echo "=== launch_indexer.sh ==="
cat /Agent/bin/launch_indexer.sh
echo ""
echo "=== flow_capd_launcher 源码 ==="
cat /root/SOC/ly_analyser_src/agent/flow/flow_capd_launcher.cpp 2>/dev/null | head -80
echo ""
echo "=== crontab ==="
crontab -l 2>/dev/null
echo ""
echo "=== systemd agent 服务 ==="
ls /etc/systemd/system/ 2>/dev/null | grep -iE "agent|index|flow|nfcap"
"""),

    ("Check libcommon NEEDED", r"""
echo "=== libcommon.so NEEDED ==="
readelf -d /lib64/libcommon.so | grep NEEDED
echo ""
echo "=== indexer NEEDED ==="
readelf -d /Agent/bin/indexer | grep NEEDED
"""),

    ("Relink libcommon without -lprotobuf", r"""
echo "=== Relink libcommon.so without -lprotobuf ==="
cd /root/SOC/ly_analyser_src/common
rm -f libcommon.so
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -10
echo "Link exit: $?"
ls -lh libcommon.so 2>/dev/null
echo ""
echo "=== New NEEDED ==="
readelf -d libcommon.so | grep NEEDED
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
