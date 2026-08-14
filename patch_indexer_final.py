import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Read full flow_indexer.h and flow_indexer.cpp
print("=== Reading flow_indexer.h ===")
cmd = "cat /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
header_content = stdout.read().decode()
print(f"Header length: {len(header_content)} chars, {header_content.count(chr(10))} lines")

print("\n=== Reading flow_indexer.cpp ===")
cmd = "cat /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
cpp_content = stdout.read().decode()
print(f"CPP length: {len(cpp_content)} chars, {cpp_content.count(chr(10))} lines")

# Also check what lines reference UpdateFinished for AI filters
print("\n=== UpdateFinished lines ===")
cmd = "grep -n 'UpdateFinished' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check lines around 320-330
print("\n=== Lines 315-335 ===")
cmd = "sed -n '315,335p' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

client.close()
