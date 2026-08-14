import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix repeated_ptr_field.h begin/end precisely", r"""
echo "=== Fix repeated_ptr_field.h ==="
python3 << 'PYEOF'
filepath = '/usr/local/include/google/protobuf/repeated_ptr_field.h'
with open(filepath, 'r') as f:
    lines = f.readlines()

# Actual structure (multi-line):
#   inline typename RepeatedPtrField<Element>::iterator
#   RepeatedPtrField<Element>::begin() {
#     return const_iterator(raw_data());   <- should be iterator
#   }
#   inline typename RepeatedPtrField<Element>::const_iterator
#   RepeatedPtrField<Element>::begin() const {
#     return const_iterator(raw_data());   <- correct
#   }

fixed = 0
for i, line in enumerate(lines):
    # Non-const begin(): line contains "::begin() {" and does NOT contain "const" after it
    if '::begin() {' in line and 'const' not in line.split('begin()')[1]:
        # Find return statement in next 3 lines
        for j in range(i+1, min(i+4, len(lines))):
            if 'return const_iterator(raw_data());' in lines[j]:
                lines[j] = lines[j].replace('return const_iterator(raw_data());', 'return iterator(raw_data());')
                print(f"Fixed non-const begin() at line {j+1}")
                fixed += 1
                break
    # Non-const end()
    if '::end() {' in line and 'const' not in line.split('end()')[1]:
        for j in range(i+1, min(i+4, len(lines))):
            if 'return const_iterator(raw_data() + size());' in lines[j]:
                lines[j] = lines[j].replace('return const_iterator(raw_data() + size());', 'return iterator(raw_data() + size());')
                print(f"Fixed non-const end() at line {j+1}")
                fixed += 1
                break

with open(filepath, 'w') as f:
    f.writelines(lines)

print(f"Total fixes: {fixed}")
PYEOF

echo ""
echo "=== Verify ==="
sed -n '1750,1772p' /usr/local/include/google/protobuf/repeated_ptr_field.h
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
