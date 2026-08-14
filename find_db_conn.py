import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check how server code initializes DB connection
print("=== auth.cpp DB init ===")
cmd = r"""
grep -n 'sql\s*=\|session\|connection\|cppdb\|getenv\|DB_\|DATABASE' /root/SOC/ly_server_src/server/auth.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check main.cpp or common for DB connection string
print("\n=== main.cpp DB init ===")
cmd2 = r"""
grep -rn 'sql\s*=\|cppdb.*session\|connection_string\|getenv.*db\|getenv.*DB\|mysql:' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check common config files
print("\n=== common config.cpp ===")
cmd3 = r"""
grep -n 'getenv\|connection\|mysql\|database\|db_' /root/SOC/ly_server_src/common/config.cpp 2>/dev/null | head -20
echo "---"
grep -n 'getenv\|connection\|mysql\|database\|db_' /root/SOC/ly_server_src/common/config.h 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check common.h for DB defines
print("\n=== common.h DB ===")
cmd4 = r"""
grep -n 'DB_\|MYSQL\|mysql\|database\|cppdb' /root/SOC/ly_server_src/common/common.h 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check what strings the auth binary has for DB
print("\n=== auth DB strings ===")
cmd5 = r"""
strings /Server/www/d/auth | grep -E 'mysql:|database|DB_|connection|cppdb|ly_server|ly_agent|127\.0\.0\.1|localhost' | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check server Makefile for any DB config
print("\n=== server Makefile ===")
cmd6 = r"""
grep -i 'db\|mysql\|database\|cppdb' /root/SOC/ly_server_src/server/Makefile | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd6, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
