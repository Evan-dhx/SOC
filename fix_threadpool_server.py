import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix threadpool.hpp in ly_server
print("=== Fixing threadpool.hpp ===")
cmd = r"""cd /root/SOC/ly_server_src/common && sed -i 's/Threadpool(int size)/Threadpool(int pool_size)/' threadpool.hpp && sed -i 's/idlThrNum = size < 1 ? 1 : size;/idlThrNum = pool_size < 1 ? 1 : pool_size;/' threadpool.hpp && sed -i 's/for (size = 0; size < idlThrNum; ++size)/for (int i = 0; i < idlThrNum; ++i)/' threadpool.hpp && echo 'Fixed threadpool.hpp'"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Verify the fix
print("\n=== Verifying fix (lines 33-37) ===")
cmd2 = r"""sed -n '33,37p' /root/SOC/ly_server_src/common/threadpool.hpp"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile common module
print("\n=== Recompiling common module ===")
cmd3 = r"""cd /root/SOC/ly_server_src/common && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -20"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

# Install common module
print("\n=== Installing common module ===")
cmd4 = r"""cd /root/SOC/ly_server_src/common && make install 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile server module
print("\n=== Recompiling server module ===")
cmd5 = r"""cd /root/SOC/ly_server_src/server && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -80"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
