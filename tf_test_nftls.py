import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    # Test nftls with full path
    ('test nftls server', '/home/Agent/bin/nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /Agent/etc/nftls.status -d 2>&1; sleep 2; ss -tlnp | grep 19996; echo "STATUS FILE:"; cat /Agent/etc/nftls.status 2>/dev/null'),
    
    # Test nftls client 
    ('test nftls client', '/home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19996 -i "默认设备" -k 43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa -d 2>&1; sleep 1; ss -tlnp | grep 9996'),
    
    # Check nftls processes
    ('nftls processes', 'ps aux | grep nftls | grep -v grep'),
    
    # Check status file after client connects
    ('status after connect', 'cat /Agent/etc/nftls.status'),
    
    # Check if nfcapd is receiving
    ('nfcapd check', 'ss -uln | grep 9995; ps aux | grep fcapd | grep -v grep'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()