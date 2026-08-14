import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch protobuf headers for GCC 11 compatibility", r"""
echo "=== Patch protobuf repeated_ptr_field.h ==="

# Fix the const iterator conversion issue in repeated_ptr_field.h
RPTF=/usr/local/include/google/protobuf/repeated_ptr_field.h

# Backup
cp $RPTF ${RPTF}.backup

# Fix begin() const - add explicit cast
sed -i 's/return iterator(raw_data());/return const_iterator(raw_data());/' $RPTF
# Fix end() const - add explicit cast  
sed -i 's/return iterator(raw_data() + size());/return const_iterator(raw_data() + size());/' $RPTF

echo "OK: repeated_ptr_field.h patched"
"""),

    ("Patch arena_impl.h for GCC 11", r"""
echo "=== Patch arena_impl.h ==="

AIH=/usr/local/include/google/protobuf/arena_impl.h
cp $AIH ${AIH}.backup

# Fix the fill() issue - cast NULL to proper pointer type
sed -i 's/std::fill(cached_block_\*, cached_block_\* + kBlockListSize, 0);/std::fill(cached_block_\*, cached_block_\* + kBlockListSize, static_cast<CachedBlock\*>(nullptr));/' $AIH

# Alternative: just add -fpermissive
echo "OK: arena_impl.h patched (or will use -fpermissive)"
"""),

    ("Add -fpermissive to Makefile and retry", r"""
echo "=== Add -fpermissive and retry ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Add -fpermissive to CXXFLAGS to work around protobuf 3.21 + GCC 11 issues
sed -i 's/CXXFLAGS=-Wall -fPIC -g -std=c++14 -DAGENT -O2/CXXFLAGS=-Wall -fPIC -g -std=c++14 -DAGENT -O2 -fpermissive/' Makefile

echo "New CXXFLAGS:"
grep "^CXXFLAGS=" Makefile

make clean
make flow_filter.a 2>&1 | tail -80
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
