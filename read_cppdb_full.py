import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find cppdb source files
print("=== cppdb source files ===")
cmd = r"""
find /root/build_deps/cppdb-0.3.1/src/ -name '*.cpp' -o -name '*.h' 2>/dev/null
echo "---"
find /usr/include/cppdb/ -type f 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the main cppdb source
print("\n=== cppdb.cpp (session) ===")
cmd2 = r"""
cat /root/build_deps/cppdb-0.3.1/src/cppdb.cpp 2>/dev/null | head -100
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read connection_info
print("\n=== connection_info.cpp ===")
cmd3 = r"""
cat /root/build_deps/cppdb-0.3.1/src/connection_info.cpp 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the mysql backend open function fully
print("\n=== mysql_backend open function ===")
cmd4 = r"""
sed -n '1155,1310p' /root/build_deps/cppdb-0.3.1/drivers/mysql_backend.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
