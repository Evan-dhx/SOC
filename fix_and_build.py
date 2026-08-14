import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix ly_strings.cpp self-reference
cmd = r"""cd /root/SOC/ly_server_src/common && sed -i 's|#include "strings.h"|#include "ly_strings.h"|' ly_strings.cpp && echo 'Fixed ly_strings.cpp' && head -5 ly_strings.cpp"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Now try to compile common module
cmd2 = r"""cd /root/SOC/ly_server_src/common && make clean 2>&1 | tail -3 && make -j4 2>&1 | tail -60"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
