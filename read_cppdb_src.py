import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read cppdb mysql_backend.cpp to understand connection string parsing
print("=== cppdb mysql_backend.cpp (connection parsing) ===")
cmd = r"""
grep -n 'read_default_group\|read_default_file\|mysql_options\|user\|password\|connect' /root/build_deps/cppdb-0.3.1/drivers/mysql_backend.cpp | head -40
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the actual connection function
print("\n=== cppdb connect function ===")
cmd2 = r"""
grep -n -A 30 'void mysql_connection::open' /root/build_deps/cppdb-0.3.1/drivers/mysql_backend.cpp | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check how cppdb parses connection string
print("\n=== cppdb connection string parsing ===")
cmd3 = r"""
grep -n -B5 -A20 'parse.*connection\|connection_string\|split.*connection' /root/build_deps/cppdb-0.3.1/drivers/mysql_backend.cpp | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check cppdb frontend for connection string format
print("\n=== cppdb frontend session ===")
cmd4 = r"""
grep -n 'read_default\|mysql:' /usr/include/cppdb/frontend.h 2>/dev/null | head -10
echo "---"
grep -rn 'read_default' /root/build_deps/cppdb-0.3.1/src/ 2>/dev/null | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
