import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Continue server compilation
print("=== Completing server module compilation ===")
cmd = r"""cd /root/SOC/ly_server_src/server && make -j4 2>&1 | tail -60"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

# Install server module
print("\n=== Installing server module ===")
cmd2 = r"""cd /root/SOC/ly_server_src/server && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# List installed files
print("\n=== Installed server files ===")
cmd3 = r"""ls -la /Server/www/d/ /Server/bin/ /Server/cmd/ 2>&1 | head -40"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
