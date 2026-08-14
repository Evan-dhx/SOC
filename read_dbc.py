import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read full dbc.cpp source
print("=== dbc.cpp full source ===")
cmd = r"""
cat /root/SOC/ly_server_src/server/dbc.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read dbc.h
print("\n=== dbc.h ===")
cmd2 = r"""
cat /root/SOC/ly_server_src/server/dbc.h
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check for any DB config in common
print("\n=== common.h DB config ===")
cmd3 = r"""
grep -n 'DB_\|MYSQL\|mysql\|database\|db_\|user\|pass\|group' /root/SOC/ly_server_src/common/common.h 2>/dev/null | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check common config.h
print("\n=== common config.h ===")
cmd4 = r"""
cat /root/SOC/ly_server_src/common/config.h 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check for environment variable names
print("\n=== env var names in dbc ===")
cmd5 = r"""
strings /Server/www/d/auth | grep -E '^[A-Z_]{3,20}$' | sort -u | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
