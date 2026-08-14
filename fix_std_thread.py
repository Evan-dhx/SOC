import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Backup and fix std_thread.h
print("=== Fixing std_thread.h ===")
cmd = r"""
cp /usr/include/c++/11/bits/std_thread.h /usr/include/c++/11/bits/std_thread.h.bak
sed -i 's/auto __depend = __null;/void (*__depend)() = nullptr;/' /usr/include/c++/11/bits/std_thread.h
echo 'Fixed std_thread.h'
grep -n '__depend' /usr/include/c++/11/bits/std_thread.h | head -5
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile server
print("\n=== Recompiling server module ===")
cmd2 = r"""cd /root/SOC/ly_server_src/server && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -80"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
