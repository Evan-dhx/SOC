import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the frontend.cpp which likely has connection string parsing
print("=== frontend.cpp ===")
cmd = r"""
cat /root/build_deps/cppdb-0.3.1/src/frontend.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Also check utils.cpp for connection string parsing
print("\n=== utils.cpp ===")
cmd2 = r"""
cat /root/build_deps/cppdb-0.3.1/src/utils.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
