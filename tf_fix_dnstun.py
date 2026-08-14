import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch dnstun_ai_filter.h", r"""
echo "=== Patch dnstun_ai_filter.h ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Check current includes
grep -n "libnfdump\|tensorflow" dnstun_ai_filter.h | head -10

# Backup
cp dnstun_ai_filter.h dnstun_ai_filter.h.backup

# Add #undef v4/v6 before TF includes
sed -i '/#include <tensorflow\/cc\/client\/client_session.h>/i \
#pragma push_macro("v4")\
#pragma push_macro("v6")\
#undef v4\
#undef v6' dnstun_ai_filter.h

# Add #pragma pop_macro after last TF include
sed -i '/#include <tensorflow\/core\/public\/session.h>/a \
#pragma pop_macro("v4")\
#pragma pop_macro("v6")' dnstun_ai_filter.h

echo "Patched dnstun_ai_filter.h"
grep -n "push_macro\|undef\|pop_macro\|tensorflow" dnstun_ai_filter.h | head -10
"""),

    ("Retry compile", r"""
echo "=== Retry compile ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -40
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
