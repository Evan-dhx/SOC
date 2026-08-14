import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find all table references in the source code
print("=== Finding all table references ===")
cmd = r"""
grep -rhoP 't_\w+' /root/SOC/ly_server_src/server/*.cpp /root/SOC/ly_server_src/common/*.cpp 2>/dev/null | sort -u | grep '^t_'
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
tables = stdout.read().decode('utf-8', errors='replace').strip()
print(tables)

# Check what tables exist
print("\n=== Current tables ===")
cmd2 = r"""
mysql -u root -p'password123' server -e "SHOW TABLES;" 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config.cpp for table usage
print("\n=== config.cpp table refs ===")
cmd3 = r"""
grep -n 't_' /root/SOC/ly_server_src/server/config.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check event.cpp for table usage
print("\n=== event.cpp table refs ===")
cmd4 = r"""
grep -n 't_' /root/SOC/ly_server_src/server/event.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check bwlist.cpp
print("\n=== bwlist.cpp table refs ===")
cmd5 = r"""
grep -n 't_' /root/SOC/ly_server_src/server/bwlist.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
