import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix boost_thread-mt to boost_thread in lib Makefile
print("=== Fixing lib/Makefile ===")
cmd = r"""cd /root/SOC/ly_server_src/lib && sed -i 's/-lboost_thread-mt/-lboost_thread/g' Makefile && grep 'boost_thread' Makefile"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Fix boost_thread-mt to boost_thread in server Makefile
print("\n=== Fixing server/Makefile ===")
cmd2 = r"""cd /root/SOC/ly_server_src/server && sed -i 's/-lboost_thread-mt/-lboost_thread/g' Makefile && grep 'boost_thread' Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile lib module
print("\n=== Recompiling lib module ===")
cmd3 = r"""cd /root/SOC/ly_server_src/lib && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -80"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
