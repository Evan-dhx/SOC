import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Install common module
print("=== Installing common module ===")
cmd = r"""cd /root/SOC/ly_server_src/common && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Check lib and server directories
print("\n=== Checking ly_server structure ===")
cmd2 = r"""ls -la /root/SOC/ly_server_src/lib/Makefile /root/SOC/ly_server_src/server/Makefile 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check lib Makefile
print("\n=== lib/Makefile (first 30 lines) ===")
cmd3 = r"""head -30 /root/SOC/ly_server_src/lib/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
