import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the device GET handler section
print("=== Device GET handler (lines 440-530) ===")
cmd = r"""
sed -n '440,530p' /root/SOC/ly_server_src/lib/config_agent.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Also read lines 140-180 for the Process flow
print("\n=== Process flow (lines 140-180) ===")
cmd2 = r"""
sed -n '140,180p' /root/SOC/ly_server_src/lib/config_agent.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
