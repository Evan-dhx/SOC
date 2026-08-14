import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Install lib module
print("=== Installing lib module ===")
cmd = r"""cd /root/SOC/ly_server_src/lib && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Check server Makefile
print("\n=== server/Makefile (first 40 lines) ===")
cmd2 = r"""head -40 /root/SOC/ly_server_src/server/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Compile server module
print("\n=== Compiling server module ===")
cmd3 = r"""cd /root/SOC/ly_server_src/server && make clean 2>&1 | tail -3 && make -j4 2>&1 | tail -100"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
