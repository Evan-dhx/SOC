import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read config.cpp to understand what tables it uses
print("=== config.cpp source ===")
cmd = r"""
cat -n /root/SOC/ly_server_src/server/config.cpp | head -100
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config_pusher for t_event_status columns
print("\n=== t_event_status refs ===")
cmd2 = r"""
grep -n 't_event_status\|event_status' /root/SOC/ly_server_src/server/config_pusher.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check gen_event for more table columns
print("\n=== gen_event table refs ===")
cmd3 = r"""
grep -n 't_event_list\|t_event_type\|t_event_level\|t_event_ignore\|t_event_data\b' /root/SOC/ly_server_src/server/gen_event.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check mo.cpp for t_mo columns
print("\n=== t_mo full schema ===")
cmd4 = r"""
grep -n 't_mo\|t_mogroup' /root/SOC/ly_server_src/server/mo.cpp | head -20
echo "---"
grep -n 't_device\|t_agent' /root/SOC/ly_server_src/server/config_pusher.cpp | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
