import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restore common to new ABI (for ly_server)
print("=== Restoring common to new ABI ===")
cmd = r"""cd /root/SOC/ly_analyser_src/common
sed -i 's/-D_GLIBCXX_USE_CXX11_ABI=0 //' Makefile
grep CXXFLAGS Makefile | head -2"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild common with new ABI
print("\n=== Rebuilding common (new ABI) ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/common && make clean 2>&1 | tail -1 && make -j4 2>&1 | tail -5 && make install 2>&1 | tail -5"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Also rebuild ly_server common with new ABI
print("\n=== Rebuilding ly_server common (new ABI) ===")
cmd3 = r"""cd /root/SOC/ly_server_src/common && make clean 2>&1 | tail -1 && make -j4 2>&1 | tail -5 && make install 2>&1 | tail -5"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Now create old-ABI static common for agent modules
print("\n=== Building old-ABI static common for agent ===")
cmd4 = r"""
# Create a copy of common source for old-ABI build
rm -rf /root/SOC/ly_analyser_src/common_oldabi
cp -r /root/SOC/ly_analyser_src/common /root/SOC/ly_analyser_src/common_oldabi
cd /root/SOC/ly_analyser_src/common_oldabi

# Add old ABI flag
sed -i 's/CXXFLAGS=-Wall -g -fPIC -std=c++1y -O2/CXXFLAGS=-Wall -g -std=c++1y -O2 -D_GLIBCXX_USE_CXX11_ABI=0/' Makefile
# Remove -fPIC since we're building static
# Remove shared lib target
grep CXXFLAGS Makefile | head -2

# Build only static lib
make clean 2>&1 | tail -1
make libcommon.a 2>&1 | tail -5
ls -la libcommon.a 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
