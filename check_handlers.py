import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# ============================================================
# Step 1: Check handlers Makefile
# ============================================================
print("=== Handlers Makefile ===")
cmd = "cat /root/SOC/ly_analyser_src/agent/handlers/Makefile"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

client.close()
