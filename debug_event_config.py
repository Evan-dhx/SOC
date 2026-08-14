import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what event_config queries
print("=== event_config GET handler ===")
cmd = r"""
grep -n -B5 -A50 'event_config\|EventConfig' /root/SOC/ly_server_src/lib/config_event.cpp | grep -B5 -A30 'case GET\|Get()' | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check what tables event_config uses
print("\n=== event_config table refs ===")
cmd2 = r"""
grep -n 't_event_config\|t_event_list\|t_event_status' /root/SOC/ly_server_src/lib/config_event.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the event_config GET SQL
print("\n=== event_config GET SQL ===")
cmd3 = r"""
grep -n 'SELECT.*t_event_config\|SELECT.*t_event_list\|SELECT.*t_event_status' /root/SOC/ly_server_src/lib/config_event.cpp | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check table structures
print("\n=== Check tables ===")
cmd4 = r"""
mysql -u root -p'password123' server << 'EOSQL'
DESCRIBE t_event_config_threshold;
DESCRIBE t_event_list;
DESCRIBE t_event_status;
EOSQL
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
