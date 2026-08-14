import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what columns the code expects
print("=== t_event_type column refs ===")
cmd = r"""
grep -n 't_event_type' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== t_event_action column refs ===")
cmd2 = r"""
grep -rn 't_event_action\|event_action' /root/SOC/ly_server_src/ 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_event.cpp SQL ===")
cmd3 = r"""
grep -n 'SELECT\|FROM\|WHERE\|INSERT\|UPDATE\|desc\|act\b' /root/SOC/ly_server_src/lib/config_event.cpp 2>/dev/null | head -40
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_class.cpp SQL ===")
cmd4 = r"""
grep -n 'desc\|act\b\|t_event' /root/SOC/ly_server_src/lib/config_class.cpp 2>/dev/null | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check actual table structures
print("\n=== Current t_event_type structure ===")
cmd5 = r"""
mysql -u root -p'password123' server -e "DESCRIBE t_event_type; DESCRIBE t_event_action; DESCRIBE t_event_level;" 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
