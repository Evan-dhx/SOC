import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check for pthread_create macro
print("=== Checking for pthread_create conflicts ===")
cmd = r"""grep -rn 'pthread_create\|pthread' /root/SOC/ly_server_src/common/*.h /root/SOC/ly_server_src/common/*.cpp 2>/dev/null | grep -v 'Binary\|.pb.' | head -20"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check common.h for any thread-related includes
print("\n=== common.h includes ===")
cmd2 = r"""head -50 /root/SOC/ly_server_src/common/common.h"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Try compiling gen_event.cpp with verbose output
print("\n=== Compiling gen_event.cpp with -E to see preprocessor ===")
cmd3 = r"""cd /root/SOC/ly_server_src/server && g++ -E gen_event.cpp -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I../common 2>&1 | grep -A5 -B5 'GTHR_ACTIVE_PROXY\|pthread_create' | head -40"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
