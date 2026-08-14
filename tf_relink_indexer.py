import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Install new libcommon.so", r"""
echo "=== Install new libcommon.so ==="
cd /root/SOC/ly_analyser_src/common
cp libcommon.so /lib64/
cp libcommon.so /usr/lib64/
ldconfig
readelf -d /lib64/libcommon.so | grep NEEDED | head -5
echo "Installed OK"
"""),

    ("Relink indexer without -lprotobuf", r"""
echo "=== Modify indexing Makefile ==="
cd /root/SOC/ly_analyser_src/agent/indexing
sed -i 's/-Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive //' Makefile
grep "LDLIBS" Makefile
echo ""
echo "=== Relink indexer ==="
rm -f indexer
make 2>&1 | tail -10
echo ""
echo "Exit: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer linked" || echo "FAIL: link failed"
echo ""
echo "=== New NEEDED ==="
readelf -d indexer 2>/dev/null | grep NEEDED
"""),

    ("Deploy AI model files", r"""
echo "=== Deploy models ==="
mkdir -p /Agent/data/models
ls -lh /root/SOC/ly_analyser_src/agent/flow/models/
cp -v /root/SOC/ly_analyser_src/agent/flow/models/*.pb /Agent/data/models/ 2>/dev/null
echo ""
ls -lh /Agent/data/models/
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
