import paramiko, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Upload updated actl.cpp
sftp = c.open_sftp()
local_path = r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp'
remote_path = '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp'
sftp.put(local_path, remote_path)
sftp.close()
print('Uploaded actl.cpp')

# Build actl on server
print()
print('=== Build actl ===')
cmd = 'cd /root/SOC/ly_analyser_src/agent/handlers && make actl 2>&1 | tail -20'
i, o, e = c.exec_command(cmd, timeout=120)
print(o.read().decode().strip()[:2000])

print()
print('=== Check actl binary ===')
i, o, e = c.exec_command('ls -la /root/SOC/ly_analyser_src/agent/handlers/actl', timeout=10)
print(o.read().decode().strip())

c.close()