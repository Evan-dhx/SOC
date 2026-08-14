import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Rebuild flow module
print("=== Rebuilding flow module ===")
cmd = r"""cd /root/SOC/ly_analyser_src/agent/flow && make clean 2>&1 | tail -2 && make flow_filter.a 2>&1 | tail -5"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild model, data, config
print("\n=== Rebuilding model/data/config ===")
cmd2 = r"""
for dir in model data config; do
  echo "--- $dir ---"
  cd /root/SOC/ly_analyser_src/agent/$dir && make clean 2>&1 | tail -1 && make -j4 2>&1 | tail -5
done
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild indexing
print("\n=== Rebuilding indexing module ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/agent/indexing && make clean 2>&1 | tail -2 && make 2>&1 | tail -30"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
