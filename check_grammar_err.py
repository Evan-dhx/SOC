import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Getting full grammar.o compile error ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Remove old grammar.o to force recompile
rm -f grammar.o

# Try to compile just grammar.o to see full error
make grammar.o 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
