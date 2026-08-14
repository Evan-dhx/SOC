import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the full config_user.cpp ParseReq and Get methods
print("=== config_user.cpp ParseReq ===")
cmd = r"""
sed -n '129,200p' /root/SOC/ly_server_src/lib/config_user.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== config_user.cpp Get ===")
cmd2 = r"""
grep -n -A50 'bool ConfigUser::Get' /root/SOC/ly_server_src/lib/config_user.cpp | head -60
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
