import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check flow Makefile for link targets
print("=== flow/Makefile targets ===")
cmd = r"""grep -E '^[a-z_]+:' /root/SOC/ly_analyser_src/agent/flow/Makefile | head -20"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Build only the library part of flow
print("\n=== Building flow_filter.a only ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/agent/flow && make flow_filter.a 2>&1 | tail -10"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Check if flow_filter.a exists
print("\n=== Checking flow_filter.a ===")
cmd3 = r"""ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Now rebuild indexing
print("\n=== Rebuilding indexing module ===")
cmd4 = r"""cd /root/SOC/ly_analyser_src/agent/indexing && make clean 2>&1 | tail -2 && make 2>&1 | tail -40"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
