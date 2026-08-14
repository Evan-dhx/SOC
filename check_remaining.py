import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check actual table structures
print("=== Check tables ===")
cmd = r"""
mysql -u root -p'password123' server << 'EOSQL'
DESCRIBE t_event_action;
DESCRIBE t_event_ignore;
DESCRIBE t_user;
EOSQL
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check what config_event.cpp queries for event_action
print("\n=== event_action query ===")
cmd2 = r"""
grep -n -B5 -A20 'event_action\|t_event_action' /root/SOC/ly_server_src/lib/config_event.cpp | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check what config_event.cpp queries for event_ignore
print("\n=== event_ignore query ===")
cmd3 = r"""
grep -n -B5 -A30 'event_ignore\|t_event_ignore' /root/SOC/ly_server_src/lib/config_event.cpp | head -80
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check what config_user.cpp queries
print("\n=== config_user query ===")
cmd4 = r"""
grep -n 'SELECT\|FROM\|t_user' /root/SOC/ly_server_src/lib/config_user.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
