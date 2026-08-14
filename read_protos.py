import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config proto files for field definitions
print("=== config_event.proto ===")
cmd = r"""
cat /root/SOC/ly_server_src/lib/config_event.proto 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_device.proto ===")
cmd2 = r"""
cat /root/SOC/ly_server_src/lib/config_device.proto 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_user.proto ===")
cmd3 = r"""
cat /root/SOC/ly_server_src/lib/config_user.proto 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_bwlist.proto ===")
cmd4 = r"""
cat /root/SOC/ly_server_src/lib/config_bwlist.proto 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_agent.proto ===")
cmd5 = r"""
cat /root/SOC/ly_server_src/lib/config_agent.proto 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
