import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Comprehensive protobuf GCC 11 patches", r"""
echo "=== Comprehensive protobuf patches ==="

# 1. Fix implicit_weak_message.h
IWM=/usr/local/include/google/protobuf/implicit_weak_message.h
cp $IWM ${IWM}.backup2 2>/dev/null
# Line 168: iterator(base().raw_data()) -> const_iterator(base().raw_data())
sed -i 's/const_iterator begin() const { return iterator(base().raw_data()); }/const_iterator begin() const { return const_iterator(base().raw_data()); }/' $IWM
sed -i 's/const_iterator end() const { return iterator(base().raw_data() + size()); }/const_iterator end() const { return const_iterator(base().raw_data() + size()); }/' $IWM
echo "Patched implicit_weak_message.h"

# 2. Fix repeated_ptr_field.h more thoroughly  
RPTF=/usr/local/include/google/protobuf/repeated_ptr_field.h
cp $RPTF ${RPTF}.backup2 2>/dev/null
# Fix all iterator -> const_iterator conversions in const methods
sed -i '/const_iterator begin() const/,/}/ s/return iterator(/return const_iterator(/g' $RPTF
sed -i '/const_iterator end() const/,/}/ s/return iterator(/return const_iterator(/g' $RPTF
echo "Patched repeated_ptr_field.h"

# 3. Fix arena_impl.h - the fill with 0 issue
AIH=/usr/local/include/google/protobuf/arena_impl.h
cp $AIH ${AIH}.backup2 2>/dev/null
# Replace the problematic fill line
sed -i 's/std::fill(cached_block_, cached_block_ + kBlockListSize, 0);/for (int i = 0; i < kBlockListSize; i++) cached_block_[i] = nullptr;/' $AIH
echo "Patched arena_impl.h"

# 4. Check for similar issues in other files
grep -rn "return iterator(raw_data" /usr/local/include/google/protobuf/*.h 2>/dev/null | grep -v backup | head -10

echo ""
echo "OK: All patches applied"
"""),

    ("Retry compile flow_filter.a", r"""
echo "=== Retry compile flow_filter.a ==="
cd /root/SOC/ly_analyser_src/agent/flow
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
