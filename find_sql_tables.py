import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find actual table names from SQL queries (FROM, INTO, UPDATE, JOIN)
print("=== SQL table names ===")
cmd = r"""
grep -rhoP '(?:FROM|INTO|UPDATE|JOIN|TABLE)\s+`?(t_\w+)`?' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | awk '{print $2}' | sort -u
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Also check the error log for missing tables
print("\n=== Missing tables from error log ===")
cmd2 = r"""
grep -oP "Table 'server\.\w+' doesn't exist" /var/log/httpd/ly_error_log | sort -u
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config.cpp more carefully for SQL
print("\n=== config.cpp SQL ===")
cmd3 = r"""
grep -n 'FROM\|INTO\|UPDATE\|SELECT\|INSERT\|CREATE' /root/SOC/ly_server_src/server/config.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check all cpp files for SQL table references
print("\n=== All SQL table refs ===")
cmd4 = r"""
grep -rn 'FROM\s*`' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
