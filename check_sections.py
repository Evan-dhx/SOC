import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# First check the event_generators section (lines 280-300)
print("=== Lines 280-305 of flow_indexer.cpp ===")
cmd = "sed -n '280,305p' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check lines 200-220 for Create calls
print("=== Lines 200-220 of flow_indexer.cpp ===")
cmd = "sed -n '200,220p' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check lines 55-65 of header
print("=== Lines 55-65 of flow_indexer.h ===")
cmd = "sed -n '55,65p' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check lines 25-32 of header
print("=== Lines 25-32 of flow_indexer.h ===")
cmd = "sed -n '25,32p' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

client.close()
