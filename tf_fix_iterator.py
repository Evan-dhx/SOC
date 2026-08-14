import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Inspect repeated_ptr_field.h begin/end methods", r"""
echo "=== Inspect begin/end methods ==="
grep -n "begin()\|end()" /usr/local/include/google/protobuf/repeated_ptr_field.h | head -20
echo ""
echo "=== Show lines 1745-1780 ==="
sed -n '1745,1780p' /usr/local/include/google/protobuf/repeated_ptr_field.h
"""),

    ("Fix repeated_ptr_field.h precisely", r"""
echo "=== Fix repeated_ptr_field.h ==="
python3 << 'PYEOF'
filepath = '/usr/local/include/google/protobuf/repeated_ptr_field.h'
with open(filepath, 'r') as f:
    lines = f.readlines()

# Fix: non-const begin() should return iterator, const begin() should return const_iterator
# Current state (after previous patch):
#   iterator begin() { return const_iterator(raw_data()); }        <- WRONG, should be iterator
#   const_iterator begin() const { return const_iterator(raw_data()); }  <- correct

for i, line in enumerate(lines):
    stripped = line.strip()
    # Non-const begin()
    if stripped == 'iterator begin() {' or stripped == 'iterator begin() {':
        # Find the return statement in the next few lines
        for j in range(i+1, min(i+5, len(lines))):
            if 'return const_iterator(raw_data());' in lines[j]:
                lines[j] = lines[j].replace('return const_iterator(raw_data());', 'return iterator(raw_data());')
                print(f"Fixed begin() at line {j+1}")
                break
    # Non-const end()
    if stripped == 'iterator end() {' or stripped == 'iterator end() {':
        for j in range(i+1, min(i+5, len(lines))):
            if 'return const_iterator(raw_data() + size());' in lines[j]:
                lines[j] = lines[j].replace('return const_iterator(raw_data() + size());', 'return iterator(raw_data() + size());')
                print(f"Fixed end() at line {j+1}")
                break

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Done patching")
PYEOF

echo ""
echo "=== Verify ==="
sed -n '1750,1775p' /usr/local/include/google/protobuf/repeated_ptr_field.h
"""),

    ("Retry compile indexer", r"""
echo "=== Retry compile indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -50
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
