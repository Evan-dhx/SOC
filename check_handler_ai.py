import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what AI/TF references exist in these files
print("=== extract_feature.cpp AI/TF references ===")
cmd = "grep -n 'dga\\|DgaFilter\\|tensorflow\\|TensorFlow\\|threat\\|mining\\|dnstun_ai' /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

print("\n=== extract_event_feature.cpp AI/TF references ===")
cmd = "grep -n 'dga\\|DgaFilter\\|tensorflow\\|TensorFlow\\|threat\\|mining\\|dnstun_ai' /root/SOC/ly_analyser_src/agent/handlers/extract_event_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Show the relevant sections
print("\n=== extract_feature.cpp includes ===")
cmd = "head -30 /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

print("\n=== extract_feature.cpp around line 450-470 ===")
cmd = "sed -n '450,475p' /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

print("\n=== extract_event_feature.cpp includes ===")
cmd = "head -30 /root/SOC/ly_analyser_src/agent/handlers/extract_event_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check extract_event_feature.cpp for TF usage
print("\n=== extract_event_feature.cpp grep TF ===")
cmd = "grep -n 'tensorflow\\|Session\\|Env\\|Status' /root/SOC/ly_analyser_src/agent/handlers/extract_event_feature.cpp | head -20"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

client.close()
