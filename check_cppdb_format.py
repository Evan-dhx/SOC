import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check cppdb connection_info parsing
print("=== cppdb connection_info parsing ===")
cmd = r"""
grep -n -B5 -A30 'connection_info::connection_info\|parse.*connection\|split.*;' /root/build_deps/cppdb-0.3.1/src/connection_info.cpp 2>/dev/null | head -80
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Also check how cppdb session constructs connection_info
print("\n=== cppdb session constructor ===")
cmd2 = r"""
grep -n -B5 -A20 'session::session.*string' /root/build_deps/cppdb-0.3.1/src/cppdb.cpp 2>/dev/null | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the connection_info header
print("\n=== connection_info.h ===")
cmd3 = r"""
cat /usr/include/cppdb/connection_info.h 2>/dev/null | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
