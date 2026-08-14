import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix CXXFLAGS in indexing Makefile", r"""
echo "=== Fix indexing Makefile CXXFLAGS ==="
cd /root/SOC/ly_analyser_src/agent/indexing

# Show current CXXFLAGS lines
grep "CXXFLAGS" Makefile

# Fix -std=c++14 -> -std=c++17 and add -fpermissive
sed -i 's/-std=c++14/-std=c++17 -fpermissive/' Makefile

echo ""
echo "After fix:"
grep "CXXFLAGS" Makefile
"""),

    ("Check arena_impl.h fix status", r"""
echo "=== Check arena_impl.h ==="
grep -n "std::fill" /usr/local/include/google/protobuf/arena_impl.h
echo ""
grep -n "cached_block_\[i\] = nullptr" /usr/local/include/google/protobuf/arena_impl.h
echo ""
echo "=== Show lines around 300-310 ==="
sed -n '298,312p' /usr/local/include/google/protobuf/arena_impl.h
"""),

    ("Fix arena_impl.h if needed", r"""
echo "=== Fix arena_impl.h ==="
AIH=/usr/local/include/google/protobuf/arena_impl.h

# Check if the fix is present; if not apply it
if ! grep -q "cached_block_\[i\] = nullptr" $AIH; then
    echo "Fix not present, applying..."
    # The actual line might use different variable names
    # Let's find the actual fill line
    grep -n "std::fill" $AIH
    
    # Try a more generic fix: replace std::fill with a loop
    python3 << 'PYEOF'
import re
with open('/usr/local/include/google/protobuf/arena_impl.h', 'r') as f:
    content = f.read()

# Replace std::fill patterns
pattern = r'std::fill\((\w+), (\w+) \+ (\w+), (\d+)\);'
replacement = r'for (int _i = 0; _i < \3; _i++) \1[_i] = nullptr;'
new_content, count = re.subn(pattern, replacement, content)
print(f"Replaced {count} fill calls")

with open('/usr/local/include/google/protobuf/arena_impl.h', 'w') as f:
    f.write(new_content)
PYEOF
else
    echo "Fix already present"
fi

# Verify
grep -n "nullptr" /usr/local/include/google/protobuf/arena_impl.h | head -5
"""),

    ("Retry compile indexer", r"""
echo "=== Retry compile indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -60
echo ""
echo "Exit code: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer generated" || echo "FAIL: indexer not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
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
