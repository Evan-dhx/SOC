import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Rebuild indexing module
print("=== Rebuilding indexing module ===")
cmd = r"""cd /root/SOC/ly_analyser_src/agent/indexing && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -60"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
