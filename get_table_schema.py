import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Get full SQL column references for each table
print("=== All column refs per table ===")
cmd = r"""
# Get all SELECT column lists and WHERE clauses for each table
grep -rn 'FROM\s*`t_' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null
echo "=== INSERT/UPDATE ==="
grep -rn 'INSERT INTO\|UPDATE\s*`t_' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | head -30
echo "=== config.cpp full SQL ==="
grep -n 'sql\s*<<\|SELECT\|FROM\|WHERE\|INSERT\|UPDATE\|DELETE' /root/SOC/ly_server_src/server/config.cpp 2>/dev/null | head -40
echo "=== mo.cpp SQL ==="
grep -n 'sql\s*<<\|SELECT\|FROM\|WHERE\|INSERT\|UPDATE\|DELETE' /root/SOC/ly_server_src/server/mo.cpp 2>/dev/null | head -20
echo "=== internalip.cpp SQL ==="
grep -n 'sql\s*<<\|SELECT\|FROM\|WHERE\|INSERT\|UPDATE\|DELETE' /root/SOC/ly_server_src/server/internalip.cpp 2>/dev/null | head -20
echo "=== bwlist.cpp SQL ==="
grep -n 'sql\s*<<\|SELECT\|FROM\|WHERE\|INSERT\|UPDATE\|DELETE' /root/SOC/ly_server_src/server/bwlist.cpp 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
