import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    # Check full config
    ('FA config GET', 'REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null | grep -E "psk:|name:\""'),
    
    # Check nftls binary 
    ('nftls binary', 'ls -la /home/Agent/bin/nftls; file /home/Agent/bin/nftls; ldd /home/Agent/bin/nftls 2>/dev/null | grep -i "ssl\|crypto\|proto"'),
    
    # Check if nftls is findable via PATH
    ('which nftls', 'which nftls 2>/dev/null; echo "---"; echo $PATH'),
    
    # Directly try to start nftls server manually
    ('test start nftls', 'kill $(lsof -ti:19996) 2>/dev/null; nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /tmp/nftls_test.status -d 2>&1; sleep 1; ss -tlnp | grep 19996'),
    
    # Check if nftls.psk exists
    ('nftls.psk', 'cat /Agent/etc/nftls.psk 2>/dev/null; echo "---"; ls -la /Agent/etc/nftls.psk 2>/dev/null'),
    
    # Check nftls status file
    ('nftls status', 'cat /Agent/etc/nftls.status 2>/dev/null; echo "---"; ls -la /Agent/etc/nftls.status 2>/dev/null'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()