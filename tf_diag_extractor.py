import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check if extractor exists
    ('extractor binary', 'ls -la /Agent/bin/extractor; file /Agent/bin/extractor'),
    # Check nfcapd current file with nfdump
    ('nfdump read test', '/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current 2>&1 | head -10'),
    # Check nfcapd closed file
    ('nfdump closed file', '/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.202608140855 2>&1 | head -10'),
    # Check directory permissions
    ('flow dir perm', 'ls -la /Agent/flow/; ls -la /Agent/flow/1/ 2>/dev/null | head -5'),
    # Run extractor directly to see what happens
    ('extractor dry run', 'cd /Agent/bin && sudo -u apache ./extractor -v 1 -t 1786669500 2>&1 | head -15'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()