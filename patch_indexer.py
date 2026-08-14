import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Patch flow_indexer.cpp to disable AI filters
print("=== Patching flow_indexer.cpp ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Backup original
cp flow_indexer.cpp flow_indexer.cpp.orig

# Add #ifdef ENABLE_AI around AI filter code
# First, let's see the structure
grep -n 'dga_\|threat_\|dnstun_ai_\|mining_\|DgaFilter\|ThreatFilter\|DnstunAIFilter\|MiningFilter' flow_indexer.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Check the header file too
print("\n=== Checking flow_indexer.h ===")
cmd2 = r"""grep -n 'dga_\|threat_\|dnstun_ai_\|mining_\|DgaFilter\|ThreatFilter\|DnstunAIFilter\|MiningFilter' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

client.close()
