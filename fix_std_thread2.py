import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the actual line in std_thread.h
print("=== Checking std_thread.h line 138 ===")
cmd = r"""sed -n '135,145p' /usr/include/c++/11/bits/std_thread.h"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Fix with the correct pattern
print("\n=== Fixing std_thread.h ===")
cmd2 = r"""
sed -i 's/auto __depend = nullptr;/void (*__depend)() = nullptr;/' /usr/include/c++/11/bits/std_thread.h
echo 'Fixed'
sed -n '135,145p' /usr/include/c++/11/bits/std_thread.h
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile gen_event only
print("\n=== Recompiling gen_event ===")
cmd3 = r"""cd /root/SOC/ly_server_src/server && rm -f gen_event && make gen_event 2>&1 | tail -30"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=120)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
