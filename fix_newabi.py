import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the current common Makefile
print("=== Current common Makefile ===")
cmd = r"""head -5 /root/SOC/ly_analyser_src/common/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Fix: Remove ALL old ABI flags and rebuild common with new ABI
print("\n=== Fixing common Makefile ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/common
sed -i 's/ -D_GLIBCXX_USE_CXX11_ABI=0//g' Makefile
head -5 Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

# Rebuild common with new ABI
print("\n=== Rebuilding common (new ABI) ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/common && make clean 2>&1 | tail -1 && make -j4 2>&1 | tail -5 && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Now remove ABI flag from ALL agent modules and rebuild
print("\n=== Removing ABI flag from agent modules ===")
cmd4 = r"""
for dir in dump utils config model data flow indexing handlers; do
  if [ -f /root/SOC/ly_analyser_src/agent/$dir/Makefile ]; then
    sed -i 's/ -D_GLIBCXX_USE_CXX11_ABI=0//g' /root/SOC/ly_analyser_src/agent/$dir/Makefile
    echo "Cleaned $dir"
  fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())

# Rebuild all agent modules with new ABI
print("\n=== Rebuilding all agent modules ===")
cmd5 = r"""
cd /root/SOC/ly_analyser_src/agent
for dir in dump config model data flow; do
  echo "=== Building $dir ==="
  cd /root/SOC/ly_analyser_src/agent/$dir
  make clean 2>&1 | tail -1
  if [ "$dir" = "flow" ]; then
    make flow_filter.a 2>&1 | tail -3
  else
    make -j4 2>&1 | tail -3
  fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=600)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(out)
if err.strip():
    print(err)

# Now rebuild indexing with full flow_filter.a
print("\n=== Rebuilding indexing with full flow_filter ===")
cmd6 = r"""
cd /root/SOC/ly_analyser_src/agent/indexing
# Restore to use full flow_filter.a
sed -i 's|flow_filter_lite.a|flow_filter.a|' Makefile
make clean 2>&1 | tail -1
make 2>&1 | tail -20
"""
stdin, stdout, stderr = client.exec_command(cmd6, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
