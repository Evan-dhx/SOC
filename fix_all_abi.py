import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check all agent module Makefiles for CXXFLAGS
print("=== Checking all agent module CXXFLAGS ===")
cmd = r"""
for dir in dump utils config model data flow indexing handlers; do
  if [ -f /root/SOC/ly_analyser_src/agent/$dir/Makefile ]; then
    echo "--- $dir ---"
    grep '^CXXFLAGS' /root/SOC/ly_analyser_src/agent/$dir/Makefile | head -3
  fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Add ABI flag to ALL agent module Makefiles
print("\n=== Adding ABI flag to all modules ===")
cmd2 = r"""
for dir in dump utils config model data flow indexing handlers; do
  if [ -f /root/SOC/ly_analyser_src/agent/$dir/Makefile ]; then
    # Add -D_GLIBCXX_USE_CXX11_ABI=0 if not already present
    if ! grep -q '_GLIBCXX_USE_CXX11_ABI' /root/SOC/ly_analyser_src/agent/$dir/Makefile; then
      sed -i '/^CXXFLAGS/s/-O2/-O2 -D_GLIBCXX_USE_CXX11_ABI=0/' /root/SOC/ly_analyser_src/agent/$dir/Makefile
      echo "Fixed $dir"
    else
      echo "Already has ABI flag: $dir"
    fi
  fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Verify
print("\n=== Verifying CXXFLAGS ===")
cmd3 = r"""
for dir in config model data flow indexing handlers; do
  echo "--- $dir ---"
  grep '^CXXFLAGS' /root/SOC/ly_analyser_src/agent/$dir/Makefile | head -2
done
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
