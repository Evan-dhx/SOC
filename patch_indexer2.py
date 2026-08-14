import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Patch flow_indexer.h
print("=== Patching flow_indexer.h ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/indexing
cp flow_indexer.h flow_indexer.h.orig

# Wrap AI filter includes
sed -i '27s|^|#ifdef ENABLE_AI\n|' flow_indexer.h
sed -i '31a #endif' flow_indexer.h

# Wrap AI filter member declarations (now shifted by 2 lines)
sed -i '61s|^|#ifdef ENABLE_AI\n|' flow_indexer.h
sed -i '65a #endif' flow_indexer.h

echo "Patched flow_indexer.h"
head -35 flow_indexer.h | tail -15
echo "..."
sed -n '58,70p' flow_indexer.h
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Patch flow_indexer.cpp
print("\n=== Patching flow_indexer.cpp ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Wrap AI Create calls
# Line 206: dga_.reset(DgaFilter::Create(...))
sed -i '206s|^|#ifdef ENABLE_AI\n    |' flow_indexer.cpp
sed -i '208a #endif' flow_indexer.cpp

# Line 210+2=212: threat_.reset(ThreatFilter::Create(...))
# After first insert, lines shifted by 2
sed -i '212s|^|#ifdef ENABLE_AI\n    |' flow_indexer.cpp
sed -i '214a #endif' flow_indexer.cpp

# Line 212+4=216: dnstun_ai_.reset(...)
sed -i '216s|^|#ifdef ENABLE_AI\n    |' flow_indexer.cpp
sed -i '218a #endif' flow_indexer.cpp

# Line 214+6=220: mining_.reset(...)
sed -i '220s|^|#ifdef ENABLE_AI\n    |' flow_indexer.cpp
sed -i '222a #endif' flow_indexer.cpp

echo "Patched Create calls"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# This approach is getting too complex with sed. Let me use Python to do the patching properly.
print("\n=== Using Python for proper patching ===")
cmd3 = r"""
cd /root/SOC/ly_analyser_src/agent/indexing
# Restore originals
cp flow_indexer.h.orig flow_indexer.h
cp flow_indexer.cpp.orig flow_indexer.cpp
echo "Restored originals"
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
