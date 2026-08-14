import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check all std::fill in arena_impl.h", r"""
echo "=== All std::fill occurrences ==="
grep -n "std::fill" /usr/local/include/google/protobuf/arena_impl.h
echo ""
echo "=== Line 300-315 ==="
sed -n '298,315p' /usr/local/include/google/protobuf/arena_impl.h
echo ""
echo "=== Check .backup files ==="
ls -la /usr/local/include/google/protobuf/arena_impl.h*
"""),

    ("Check if there are multiple protobuf include paths", r"""
echo "=== Find all arena_impl.h on system ==="
find / -name "arena_impl.h" -path "*protobuf*" 2>/dev/null
echo ""
echo "=== Check /usr/include (system protobuf?) ==="
ls /usr/include/google/protobuf/arena_impl.h 2>/dev/null || echo "not in /usr/include"
"""),

    ("Preprocess test to see which file is used", r"""
echo "=== Preprocess test ==="
cd /root/SOC/ly_analyser_src/agent/data
echo '#include "unqlite_db.h"' > /tmp/test_pre.cpp
g++ -E -I. -I../../common -I/usr/include -I/usr/local/include /tmp/test_pre.cpp 2>/dev/null | grep -n "arena_impl.h" | head -5
echo ""
echo "=== Show the fill line as preprocessed ==="
g++ -E -I. -I../../common -I/usr/include -I/usr/local/include /tmp/test_pre.cpp 2>/dev/null | grep -A2 -B2 "std::fill" | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
