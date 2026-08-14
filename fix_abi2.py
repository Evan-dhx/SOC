import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restore old ABI flag in all modules
print("=== Restoring old ABI flag ===")
cmd = r"""
for dir in flow indexing model data config handlers; do
  if [ -f /root/SOC/ly_analyser_src/agent/$dir/Makefile ]; then
    sed -i 's/-std=c++14 -DAGENT/-std=c++14 -D_GLIBCXX_USE_CXX11_ABI=0 -DAGENT/' /root/SOC/ly_analyser_src/agent/$dir/Makefile
    sed -i 's/-std=c++11 -DAGENT/-std=c++11 -D_GLIBCXX_USE_CXX11_ABI=0 -DAGENT/' /root/SOC/ly_analyser_src/agent/$dir/Makefile
    echo "Fixed $dir"
  fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check the indexing Makefile link line
print("\n=== Verifying indexing Makefile ===")
cmd2 = r"""grep -E 'CXXFLAGS|indexer:' /root/SOC/ly_analyser_src/agent/indexing/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild flow module with old ABI
print("\n=== Rebuilding flow module ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/agent/flow && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -10"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild indexing module with old ABI and fixed link order
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
