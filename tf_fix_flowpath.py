import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix: restart nfcapd with correct flow path
cmds = [
    # Kill old nfcapd
    ('pkill nfcapd', 'pkill -9 nfcapd 2>/dev/null; sleep 2'),
    # Start nfcapd with /Agent/flow/1 path (matching indexer config)
    ('start nfcapd', 'mkdir -p /Agent/flow/1; /Agent/bin/nfcapd -w -D -p 9995 -l /Agent/flow/1 -z -b 0.0.0.0 2>&1; sleep 3; ps -e | grep fcapd'),
    # Check listening
    ('port check', 'ss -uln | grep 9995'),
    # Restart tsensor to ensure fresh data
    ('restart tsensor', 'systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor'),
    # Check chain
    ('chain check', 'ps -e | grep tsensor; ps -e | grep nftls; ps -e | grep fcapd'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:200]}')

# Wait for data accumulation
print('\n等待 60 秒收流...')
time.sleep(60)

# Verify
cmds2 = [
    ('nfcapd files', 'ls -la /Agent/flow/1/ 2>/dev/null | tail -5'),
    ('restart indexer', 'pkill -9 extractor 2>/dev/null; pkill -9 indexer 2>/dev/null; sleep 2; cd /Agent/bin; setsid bash launch_indexer.sh > /tmp/indexer2.log 2>&1 &; sleep 10; ps -e | grep -E "indexer|extract" | head -3'),
    ('indexer log', 'tail -10 /tmp/indexer2.log 2>/dev/null'),
    ('check db', 'mysql -uroot -ppassword123 ly_server -e "SELECT count(1) as cnt FROM t_feature" 2>/dev/null'),
]

for label, cmd in cmds2:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')

time.sleep(30)
for label, cmd in [
    ('indexer log after', 'tail -5 /tmp/indexer2.log 2>/dev/null'),
    ('feature db count', 'mysql -uroot -ppassword123 ly_server -e "SELECT count(1) as cnt FROM t_feature" 2>/dev/null'),
    ('ti db count', 'mysql -uroot -ppassword123 ly_server -e "SELECT count(1) as cnt FROM t_ti" 2>/dev/null'),
]:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:200]}')
c.close()