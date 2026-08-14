import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the event_action GET handler
print("=== event_action GET handler ===")
cmd = r"""
grep -n -B10 -A40 'ProcessAction\|EventAction' /root/SOC/ly_server_src/lib/config_event.cpp | grep -A40 'case GET' | head -50
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the event_ignore GET handler
print("\n=== event_ignore GET handler ===")
cmd2 = r"""
sed -n '1100,1180p' /root/SOC/ly_server_src/lib/config_event.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the EventAction proto definition
print("\n=== EventAction proto ===")
cmd3 = r"""
grep -A20 'EventAction' /root/SOC/ly_server_src/lib/config_event.proto
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the EventIgnore proto definition
print("\n=== EventIgnore proto ===")
cmd4 = r"""
grep -A20 'EventIgnore\|Ignore' /root/SOC/ly_server_src/lib/config_event.proto
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
