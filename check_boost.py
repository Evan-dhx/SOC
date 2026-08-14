import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check available boost thread libraries
print("=== Available boost thread libraries ===")
cmd = r"""find /usr/lib64 /usr/lib /usr/local/lib -name 'libboost_thread*' 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check all boost libraries
print("\n=== All boost libraries ===")
cmd2 = r"""ls /usr/lib64/libboost_* 2>/dev/null | head -30"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
