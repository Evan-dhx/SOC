import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the config service files to understand what the frontend sends
print("=== config-agent.js ===")
cmd = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-agent.js
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config-mo.js ===")
cmd2 = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-mo.js
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config-event.js ===")
cmd3 = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-event.js
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config-bwlist.js ===")
cmd4 = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-bwlist.js
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config-internal.js ===")
cmd5 = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-internal.js
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config-user.js ===")
cmd6 = r"""
cat /root/SOC/ly_vis/packages/std/src/service/api/config-user.js
"""
stdin, stdout, stderr = client.exec_command(cmd6, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
