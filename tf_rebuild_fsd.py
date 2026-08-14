import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('sync fsd.cpp', 'cd /root/SOC/ly_analyser_src/handlers && cat > fsd.cpp << \'ENDOFFILE\''),
    ('sync actl.cpp', 'cd /root/SOC/ly_analyser_src/handlers && cat > actl.cpp << \'ENDOFFILE\''),
]:
    print(f'\n=== {label} ===')
    sftp = client.open_sftp()
    
    if label == 'sync fsd.cpp':
        local_path = 'd:\\QorderProject\\SOC\\ly_analyser\\src\\agent\\handlers\\fsd.cpp'
        remote_path = '/root/SOC/ly_analyser_src/handlers/fsd.cpp'
    else:
        local_path = 'd:\\QorderProject\\SOC\\ly_analyser\\src\\agent\\handlers\\actl.cpp'
        remote_path = '/root/SOC/ly_analyser_src/handlers/actl.cpp'
    
    sftp.put(local_path, remote_path)
    sftp.close()
    print('synced ok')
client.close()
print('\nFiles synced, now recompiling...')

# Now recompile via SSH
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('check synced files', 'md5sum /root/SOC/ly_analyser_src/handlers/fsd.cpp /root/SOC/ly_analyser_src/handlers/actl.cpp | head -2'),
    ('compile fsd', 'cd /root/SOC/ly_analyser_src && make handlers 2>&1 | tail -20'),
    ('check compiled', 'ls -la /root/SOC/ly_analyser_src/build/handlers/fsd /root/SOC/ly_analyser_src/build/handlers/actl 2>/dev/null; echo "---"; file /root/SOC/ly_analyser_src/build/handlers/fsd 2>/dev/null'),
    ('deploy fsd', 'pkill -x fsd 2>/dev/null; sleep 1; cp /root/SOC/ly_analyser_src/build/handlers/fsd /home/Agent/bin/ 2>/dev/null; cp /root/SOC/ly_analyser_src/build/handlers/actl /home/Agent/cmd/ 2>/dev/null; ls -la /home/Agent/bin/fsd /home/Agent/cmd/actl'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client2.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')

# Start fsd
for label, cmd in [
    ('start fsd', '/home/Agent/bin/fsd > /dev/null 2>&1 &; sleep 2; ps aux | grep fsd | grep -v grep | head -2'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client2.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'STDERR: {err[:500]}')
    print('')

client2.close()