import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check indexing Makefile
print("=== indexing/Makefile ===")
cmd = r"""cat /root/SOC/ly_analyser_src/agent/indexing/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check agent Makefile
print("\n=== agent/Makefile ===")
cmd2 = r"""cat /root/SOC/ly_analyser_src/agent/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check what libraries exist in flow
print("\n=== flow library ===")
cmd3 = r"""ls -la /root/SOC/ly_analyser_src/agent/flow/*.a 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
