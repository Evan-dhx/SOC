import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check exact structure around DGA case
print("=== Lines 450-490 of ORIGINAL extract_feature.cpp ===")
cmd = "sed -n '450,490p' /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp.orig"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Also check current patched version
print("\n=== Lines 450-490 of PATCHED extract_feature.cpp ===")
cmd = "sed -n '450,490p' /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

client.close()
