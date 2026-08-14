import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix byte typedef conflict in md5.h", r"""
echo "=== Fix byte typedef conflict ==="
cd /root/SOC/ly_analyser_src/common

# Backup
cp md5.h md5.h.backup

# In C++17, std::byte conflicts with typedef unsigned char byte
# Solution: use a unique name for the typedef
sed -i 's/typedef unsigned char byte;/typedef unsigned char md5_byte_t;/' md5.h
sed -i 's/\bbyte\b/md5_byte_t/g' md5.h

# Restore the typedef line (it was already changed)
echo "Patched md5.h"
head -15 md5.h
echo "..."
grep "md5_byte_t" md5.h | head -10
"""),

    ("Check if byte is used in other files that include md5.h", r"""
echo "=== Check byte usage in other files ==="
# Check files that include md5.h and might use 'byte'
grep -rn "\bbyte\b" /root/SOC/ly_analyser_src/common/md5.h /root/SOC/ly_analyser_src/common/md5.cpp 2>/dev/null | grep -v "md5_byte_t" | grep -v backup | head -10
echo ""
# Check if any other file uses 'byte' from md5.h
grep -rn "\bbyte\b" /root/SOC/ly_analyser_src/agent/flow/*.cpp /root/SOC/ly_analyser_src/agent/flow/*.h 2>/dev/null | grep -v "md5_byte_t" | grep -v "tensorflow" | grep -v backup | head -10
echo ""
grep -rn "\bbyte\b" /root/SOC/ly_analyser_src/common/*.cpp /root/SOC/ly_analyser_src/common/*.h 2>/dev/null | grep -v "md5_byte_t" | grep -v "pb\." | grep -v backup | head -10
"""),

    ("Also fix malice_url_filter.h (sed failed due to cd)", r"""
echo "=== Fix malice_url_filter.h ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Check if it was already patched
grep "push_macro" malice_url_filter.h | head -2
if [ $? -ne 0 ]; then
    echo "Not patched yet, applying..."
    cp malice_url_filter.h malice_url_filter.h.backup 2>/dev/null
    
    sed -i '/#include <tensorflow\/cc\/client\/client_session.h>/i \
#pragma push_macro("v4")\
#pragma push_macro("v6")\
#undef v4\
#undef v6' malice_url_filter.h
    
    sed -i '/#include <tensorflow\/core\/public\/session.h>/a \
#pragma pop_macro("v4")\
#pragma pop_macro("v6")' malice_url_filter.h
    
    echo "Patched"
else
    echo "Already patched"
fi
"""),

    ("Retry compile", r"""
echo "=== Retry compile flow_filter.a ==="
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
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
