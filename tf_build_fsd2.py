import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Sync files
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
for local, remote in [
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\fsd.cpp', '/root/SOC/ly_analyser_src/agent/handlers/fsd.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp', '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp'),
]:
    sftp.put(local, remote)
    print(f'Synced: {local} -> {remote}')
sftp.close()
client.close()

# Compile and deploy
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('compile fsd', 'cd /root/SOC/ly_analyser_src/agent/handlers; rm -f fsd.o actl.o; make fsd actl 2>&1 | tail -20'),
    ('check', 'ls -la fsd actl'),
    ('deploy', 'pkill -x fsd 2>/dev/null; sleep 1; cp fsd /home/Agent/bin/; cp actl /home/Agent/cmd/; echo "=== deployed ==="; ls -la /home/Agent/bin/fsd /home/Agent/cmd/actl'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client2.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client2.close()