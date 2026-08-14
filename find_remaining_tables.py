import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check t_event_action and t_cfg_mo references
print("=== t_event_action refs ===")
cmd = r"""
grep -rn 't_event_action\|t_cfg_mo\|t_asset' /root/SOC/ly_server_src/server/*.cpp /root/SOC/ly_server_src/common/*.cpp 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config_class.h for table names
print("\n=== config_class ===")
cmd2 = r"""
cat /root/SOC/ly_server_src/lib/config_class.h 2>/dev/null | head -50
echo "---"
ls /root/SOC/ly_server_src/lib/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check event_feature.cpp for t_event_action
print("\n=== event_feature table refs ===")
cmd3 = r"""
grep -n 't_event_action\|t_event_type\|FROM\|INSERT\|UPDATE' /root/SOC/ly_server_src/server/event_feature.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check evidence.cpp
print("\n=== evidence table refs ===")
cmd4 = r"""
grep -n 't_\|FROM\|INSERT\|SELECT' /root/SOC/ly_server_src/server/evidence.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check sctl.cpp
print("\n=== sctl table refs ===")
cmd5 = r"""
grep -n 't_\|FROM\|INSERT\|SELECT' /root/SOC/ly_server_src/server/sctl.cpp | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
