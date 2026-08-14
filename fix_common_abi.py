import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check common Makefile
print("=== ly_analyser common/Makefile ===")
cmd = r"""head -10 /root/SOC/ly_analyser_src/common/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Add ABI flag to common Makefile
print("\n=== Adding ABI flag to common/Makefile ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/common && sed -i 's/CXXFLAGS=-Wall -g -fPIC -std=c++1y -O2/CXXFLAGS=-Wall -g -fPIC -std=c++1y -O2 -D_GLIBCXX_USE_CXX11_ABI=0/' Makefile && grep CXXFLAGS Makefile | head -3"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild common
print("\n=== Rebuilding common module ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/common && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -10"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
print(stdout.read().decode())
print(stderr.read().decode())

# Install common
print("\n=== Installing common module ===")
cmd4 = r"""cd /root/SOC/ly_analyser_src/common && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Verify symbols
print("\n=== Verifying symbols ===")
cmd5 = r"""nm /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null | grep 'ipnum_to_ipstr' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
