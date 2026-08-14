import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check for strings.h conflicts in lib
print("=== Checking for strings.h in lib ===")
cmd = r"""cd /root/SOC/ly_server_src/lib && ls -la strings.h ly_strings.h 2>&1; echo '---'; grep -l 'strings.h' *.cpp *.h 2>/dev/null | head -10"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Compile lib module
print("\n=== Compiling lib module ===")
cmd2 = r"""cd /root/SOC/ly_server_src/lib && make clean 2>&1 | tail -3 && make -j4 2>&1 | tail -80"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
