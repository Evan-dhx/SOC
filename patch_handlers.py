import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# ============================================================
# Patch extract_feature.cpp
# ============================================================
print("=== Patching extract_feature.cpp ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/handlers
cp extract_feature.cpp extract_feature.cpp.orig 2>/dev/null || true

python3 << 'PYEOF'
with open("extract_feature.cpp", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Wrap #include "../flow/dga_filter.h" at line 24 (0-indexed 23)
    if i == 23 and 'dga_filter.h' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append("#endif\n")
        i += 1
        continue
    
    # Wrap DGA case block (lines 454-463, 0-indexed 453-462)
    if i == 453 and 'case feature::FeatureReq::DGA:' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        # Add all lines of the DGA case block until break + }
        j = i
        while j < len(lines):
            new_lines.append(lines[j])
            if 'break;' in lines[j] and j > i:
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
print("Patched extract_feature.cpp")
PYEOF

grep -n 'ENABLE_AI' extract_feature.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Patch extract_event_feature.cpp
# ============================================================
print("\n=== Patching extract_event_feature.cpp ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/agent/handlers
cp extract_event_feature.cpp extract_event_feature.cpp.orig 2>/dev/null || true

python3 << 'PYEOF'
with open("extract_event_feature.cpp", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Wrap AI includes (lines 19, 23, 24 - 0-indexed 18, 22, 23)
    if i == 18 and 'dga_filter.h' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append("#endif\n")
        i += 1
        continue
    
    if i == 22 and 'threat_filter.h' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append(lines[i+1])  # mining_filter.h
        new_lines.append("#endif\n")
        i += 2
        continue
    
    # Wrap DGA block (around line 155)
    if 'DgaFilter::Create' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        # Include lines from unique_ptr declaration to break
        new_lines.append(line)
        j = i + 1
        while j < len(lines):
            new_lines.append(lines[j])
            if 'break;' in lines[j]:
                j += 1
                break
            j += 1
        new_lines.append("#endif\n")
        i = j
        continue
    
    # Wrap Threat block
    if 'ThreatFilter::Create' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        j = i + 1
        while j < len(lines):
            new_lines.append(lines[j])
            if 'break;' in lines[j]:
                j += 1
                break
            j += 1
        new_lines.append("#endif\n")
        i = j
        continue
    
    # Wrap Mining block
    if 'MiningFilter::Create' in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        j = i + 1
        while j < len(lines):
            new_lines.append(lines[j])
            if 'break;' in lines[j]:
                j += 1
                break
            j += 1
        new_lines.append("#endif\n")
        i = j
        continue
    
    new_lines.append(line)
    i += 1

with open("extract_event_feature.cpp", "w") as f:
    f.writelines(new_lines)
print("Patched extract_event_feature.cpp")
PYEOF

grep -n 'ENABLE_AI' extract_event_feature.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Rebuild handlers
# ============================================================
print("\n=== Rebuilding handlers ===")
cmd3 = r"""
cd /root/SOC/ly_analyser_src/agent/handlers
make clean 2>/dev/null
make 2>&1 | tail -40
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
