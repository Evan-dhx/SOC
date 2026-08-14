import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
# Sync fsd.cpp and actl.cpp via sftp
for local, remote in [
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\fsd.cpp', '/root/SOC/ly_analyser_src/agent/handlers/fsd.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp', '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp'),
]:
    sftp.put(local, remote)
    print(f'Synced {local} -> {remote}')
sftp.close()
client.close()
print('All files synced!')