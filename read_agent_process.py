import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find the Process method and device query in config_agent.cpp
print("=== Process method and device query ===")
cmd = r"""
grep -n 'Process\|_isDevice\|target.*device\|t_device\|SELECT.*FROM.*t_device\|SELECT.*FROM.*t_agent' /root/SOC/ly_server_src/lib/config_agent.cpp | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the Process method
print("\n=== Process method (lines 30-200) ===")
cmd2 = r"""
sed -n '30,200p' /root/SOC/ly_server_src/lib/config_agent.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the device GET section
print("\n=== Device GET section ===")
cmd3 = r"""
grep -n -A 50 'isDevice.*get\|_isDevice.*GET\|case.*GET' /root/SOC/ly_server_src/lib/config_agent.cpp | head -80
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
