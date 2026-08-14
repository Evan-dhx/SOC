import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check if we can build on server
i, o, e = c.exec_command('which yarn 2>/dev/null; npm list -g lerna 2>/dev/null | head -3', timeout=30)
print(o.read().decode()[:300])
err = e.read().decode()[:200]
if err: print(f'ERR: {err}')

# Check if we can copy source to server and build
i, o, e = c.exec_command('df -h /root/ | tail -1', timeout=30)
print('Disk:', o.read().decode()[:100])
c.close()