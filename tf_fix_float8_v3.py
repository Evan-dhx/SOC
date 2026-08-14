import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix float8.h - use static_cast instead of to_float", r"""
echo "=== Fix float8.h patch ==="
F8=/usr/local/include/tf/tensorflow/tsl/platform/float8.h

# Replace all to_float() calls with static_cast<float>(...)
sed -i 's/from\.to_float()/static_cast<float>(from)/g' $F8

echo "Fixed to_float -> static_cast<float>"
grep "static_cast<float>(from)" $F8 | head -5

# Also need to fix md5.cpp which still uses 'byte' instead of 'md5_byte_t'
echo ""
echo "=== Fix md5.cpp ==="
cd /root/SOC/ly_analyser_src/common
cp md5.cpp md5.cpp.backup 2>/dev/null
sed -i 's/\bbyte\b/md5_byte_t/g' md5.cpp
echo "Fixed md5.cpp"
grep "md5_byte_t" md5.cpp | head -5
"""),

    ("Retry compile", r"""
echo "=== Retry compile ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -60
echo ""
echo "Exit code: $?"
ls -lh flow_filter.a 2>/dev/null && echo "OK: flow_filter.a generated" || echo "FAIL: flow_filter.a not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
