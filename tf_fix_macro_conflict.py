import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch dga_filter.h - undef conflicting macros before TF includes", r"""
echo "=== Patch dga_filter.h ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Restore from backup first
cp dga_filter.h.backup dga_filter.h 2>/dev/null

# Insert #undef v4/v6 before TF includes
# The TF includes start at line 19: #include <tensorflow/cc/client/client_session.h>
# We need to add #undef v4 and #undef v6 before that line

sed -i '/#include <tensorflow\/cc\/client\/client_session.h>/i \
// Undefine macroses from nffile.h that conflict with absl/TF headers\n\
#pragma push_macro("v4")\n\
#pragma push_macro("v6")\n\
#undef v4\n\
#undef v6' dga_filter.h

# Add #pragma pop_macro after the last TF include
sed -i '/#include <tensorflow\/core\/public\/session.h>/a \
#pragma pop_macro("v4")\n\
#pragma pop_macro("v6")' dga_filter.h

echo "Patched dga_filter.h"
head -30 dga_filter.h
"""),

    ("Also patch malice_url_filter.h if it has same issue", r"""
echo "=== Check malice_url_filter.h ==="
grep -n "libnfdump\|tensorflow" /root/SOC/ly_analyser_src/agent/flow/malice_url_filter.h 2>/dev/null | head -10
echo ""
# If it also includes both nfdump and TF, apply same fix
if grep -q "libnfdump" /root/SOC/ly_analyser_src/agent/flow/malice_url_filter.h 2>/dev/null; then
    echo "malice_url_filter.h also has nfdump include - patching"
    cp malice_url_filter.h malice_url_filter.h.backup 2>/dev/null
    
    sed -i '/#include <tensorflow\/cc\/client\/client_session.h>/i \
#pragma push_macro("v4")\n\
#pragma push_macro("v6")\n\
#undef v4\n\
#undef v6' malice_url_filter.h
    
    sed -i '/#include <tensorflow\/core\/public\/session.h>/a \
#pragma pop_macro("v4")\n\
#pragma pop_macro("v6")' malice_url_filter.h
    
    echo "Patched malice_url_filter.h"
else
    echo "malice_url_filter.h does not include nfdump - no patch needed"
fi
"""),

    ("Also need to fix indexing Makefile C++17", r"""
echo "=== Update indexing Makefile to C++17 ==="
cd /root/SOC/ly_analyser_src/agent/indexing
cp Makefile Makefile.backup 2>/dev/null
sed -i 's/-std=c++1y/-std=c++17/' Makefile
echo "New CXXFLAGS:"
grep "^CXXFLAGS=" Makefile
"""),

    ("Retry compile flow_filter.a", r"""
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
