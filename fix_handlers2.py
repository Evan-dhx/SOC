import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix extract_feature.cpp - restore original and re-patch correctly
print("=== Fixing extract_feature.cpp ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/handlers

# Restore from original backup
cp extract_feature.cpp.orig extract_feature.cpp

python3 << 'PYEOF'
with open("extract_feature.cpp", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Wrap #include "../flow/dga_filter.h"
    if 'dga_filter.h' in line and '#include' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append("#endif\n")
        i += 1
        continue
    
    # Wrap DGA case block - match "case feature::FeatureReq::DGA:"
    if 'case feature::FeatureReq::DGA:' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)  # case line
        # Now find the closing } of this case block
        # Structure: case ...: { ... break; }
        j = i + 1
        brace_count = 0
        found_open = False
        while j < len(lines):
            new_lines.append(lines[j])
            if '{' in lines[j]:
                brace_count += lines[j].count('{')
                found_open = True
            if '}' in lines[j]:
                brace_count -= lines[j].count('}')
            if found_open and brace_count == 0:
                j += 1
                break
            j += 1
        new_lines.append("#endif\n")
        i = j
        continue
    
    new_lines.append(line)
    i += 1

with open("extract_feature.cpp", "w") as f:
    f.writelines(new_lines)
print("Patched extract_feature.cpp correctly")
PYEOF

echo "=== Verify DGA block ==="
grep -n 'ENABLE_AI\|DGA\|dga_filter\|DgaFilter' extract_feature.cpp
echo ""
echo "=== Lines around DGA block ==="
grep -n -A1 -B1 'ENABLE_AI' extract_feature.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Rebuild handlers
print("\n=== Rebuilding handlers ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make clean 2>/dev/null
make 2>&1 | tail -30
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
