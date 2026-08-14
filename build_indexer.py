import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# ============================================================
# Step 1: Patch flow_indexer.h with #ifdef ENABLE_AI
# ============================================================
print("=" * 60)
print("Step 1: Patching flow_indexer.h")
print("=" * 60)

patch_header = r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Ensure we have original backup
cp flow_indexer.h.orig flow_indexer.h 2>/dev/null || true

python3 << 'PYEOF'
with open("flow_indexer.h", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Wrap AI includes (lines 27-30, 0-indexed 26-29)
    if i == 26 and "dga_filter.h" in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(lines[i])    # dga_filter.h
        new_lines.append(lines[i+1])  # threat_filter.h
        new_lines.append(lines[i+2])  # dnstun_ai_filter.h
        new_lines.append(lines[i+3])  # mining_filter.h
        new_lines.append("#endif\n")
        i += 4
        continue
    
    # Wrap AI member declarations (lines 59-62, 0-indexed 58-61)
    if i == 58 and "DgaFilter" in line and "dga_" in line:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(lines[i])    # dga_
        new_lines.append(lines[i+1])  # threat_
        new_lines.append(lines[i+2])  # dnstun_ai_
        new_lines.append(lines[i+3])  # mining_
        new_lines.append("#endif\n")
        i += 4
        continue
    
    new_lines.append(line)
    i += 1

with open("flow_indexer.h", "w") as f:
    f.writelines(new_lines)

print("Patched flow_indexer.h successfully")
PYEOF

echo "=== Verify header patches ==="
grep -n 'ENABLE_AI\|dga_filter\|threat_filter\|dnstun_ai_filter\|mining_filter\|DgaFilter\|ThreatFilter\|DnstunAIFilter\|MiningFilter' flow_indexer.h
"""

stdin, stdout, stderr = client.exec_command(patch_header, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

# ============================================================
# Step 2: Patch flow_indexer.cpp with #ifdef ENABLE_AI
# ============================================================
print("\n" + "=" * 60)
print("Step 2: Patching flow_indexer.cpp")
print("=" * 60)

patch_cpp = r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Ensure we have original backup
cp flow_indexer.cpp.orig flow_indexer.cpp 2>/dev/null || true

python3 << 'PYEOF'
with open("flow_indexer.cpp", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Wrap AI Create calls (4 blocks of 2 lines each)
    # dga_ Create: "if(filters_flag.find("dga")..." + "dga_.reset(...)"
    if 'filters_flag.find("dga")' in stripped and 'dga' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)       # if line
        new_lines.append(lines[i+1]) # reset line
        new_lines.append("#endif\n")
        i += 2
        continue
    
    # threat_ Create
    if 'filters_flag.find("threat")' in stripped and 'threat' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append(lines[i+1])
        new_lines.append("#endif\n")
        i += 2
        continue
    
    # dnstun_ai_ Create
    if 'filters_flag.find("dnstun_ai")' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append(lines[i+1])
        new_lines.append("#endif\n")
        i += 2
        continue
    
    # mining_ Create
    if 'filters_flag.find("mining")' in stripped and 'mining' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)
        new_lines.append(lines[i+1])
        new_lines.append("#endif\n")
        i += 2
        continue
    
    # Wrap AI event_generators block (lines 286-297, 4 else-if blocks)
    if 'Event::DGA && dga_' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        # 3 lines for DGA
        new_lines.append(line)
        new_lines.append(lines[i+1])
        new_lines.append(lines[i+2])
        # 3 lines for THREAT
        new_lines.append(lines[i+3])
        new_lines.append(lines[i+4])
        new_lines.append(lines[i+5])
        # 3 lines for DNSTUN_AI
        new_lines.append(lines[i+6])
        new_lines.append(lines[i+7])
        new_lines.append(lines[i+8])
        # 3 lines for MINING
        new_lines.append(lines[i+9])
        new_lines.append(lines[i+10])
        new_lines.append(lines[i+11])
        new_lines.append("#endif\n")
        i += 12
        continue
    
    # Wrap AI UpdateFinished (lines 321-324, 4 lines)
    if 'dga_)' in stripped and 'UpdateFinished' in stripped and 'DgaFilter' in stripped:
        new_lines.append("#ifdef ENABLE_AI\n")
        new_lines.append(line)       # dga_
        new_lines.append(lines[i+1]) # threat_
        new_lines.append(lines[i+2]) # dnstun_ai_
        new_lines.append(lines[i+3]) # mining_
        new_lines.append("#endif\n")
        i += 4
        continue
    
    new_lines.append(line)
    i += 1

with open("flow_indexer.cpp", "w") as f:
    f.writelines(new_lines)

print("Patched flow_indexer.cpp successfully")
PYEOF

echo "=== Verify cpp patches ==="
grep -n 'ENABLE_AI' flow_indexer.cpp
"""

stdin, stdout, stderr = client.exec_command(patch_cpp, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

# ============================================================
# Step 3: Rebuild flow_filter.a without AI filter objects
# ============================================================
print("\n" + "=" * 60)
print("Step 3: Rebuilding flow_filter.a without AI objects")
print("=" * 60)

rebuild_filter = r"""
cd /root/SOC/ly_analyser_src/agent/flow

# List all .o files currently in flow_filter.a
echo "=== Objects in current flow_filter.a ==="
ar t flow_filter.a | head -30

# Create new flow_filter without AI objects
echo "=== Creating flow_filter_noai.a ==="
# Extract all objects
mkdir -p /tmp/flow_objs
cd /tmp/flow_objs
rm -f *.o
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter.a

# List all objects
echo "All objects:"
ls *.o

# Remove AI filter objects
rm -f dga_filter.o threat_filter.o dnstun_ai_filter.o mining_filter.o
echo "After removing AI objects:"
ls *.o

# Create new archive
ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a *.o
echo "Created flow_filter_noai.a"
ls -lh /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a

# Cleanup
cd /root/SOC/ly_analyser_src/agent/flow
rm -rf /tmp/flow_objs
"""

stdin, stdout, stderr = client.exec_command(rebuild_filter, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

# ============================================================
# Step 4: Update indexing Makefile - use flow_filter_noai.a, remove TF libs
# ============================================================
print("\n" + "=" * 60)
print("Step 4: Updating indexing Makefile")
print("=" * 60)

fix_makefile = r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Replace flow_filter_mixed.a with flow_filter_noai.a
sed -i 's|flow_filter_mixed.a|flow_filter_noai.a|g' Makefile

# Remove TensorFlow library links
sed -i 's|-ltensorflow_cc -ltensorflow_framework||g' Makefile

echo "=== Updated Makefile ==="
cat Makefile
"""

stdin, stdout, stderr = client.exec_command(fix_makefile, timeout=15)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

# ============================================================
# Step 5: Compile indexer
# ============================================================
print("\n" + "=" * 60)
print("Step 5: Compiling indexer")
print("=" * 60)

compile_cmd = r"""
cd /root/SOC/ly_analyser_src/agent/indexing
make clean 2>/dev/null
make 2>&1 | tail -30
"""

stdin, stdout, stderr = client.exec_command(compile_cmd, timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

client.close()
