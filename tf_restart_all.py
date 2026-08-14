import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    # Step 1: Kill stale processes
    ('清理旧进程', 'pkill -x nftls 2>/dev/null; pkill -x tsensor 2>/dev/null; sleep 2; ps -e | grep -c nftls; ps -e | grep -c tsensor'),
    
    # Step 2: Start nfcapd
    ('启动 nfcapd', 'mkdir -p /data/flow/1; nfcapd -w -D -p 9995 -l /data/flow/1 -z -b 0.0.0.0 2>&1; sleep 2; ps -e | grep fcapd'),
    
    # Step 3: Write psk file
    ('写入 PSK 文件', 'echo "默认设备:43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa" > /Agent/etc/nftls.psk; chmod 600 /Agent/etc/nftls.psk; wc -c /Agent/etc/nftls.psk'),
    
    # Step 4: Start nftls server
    ('启动 nftls server', 'rm -f /Agent/etc/nftls.status; /home/Agent/bin/nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /Agent/etc/nftls.status -d 2>&1; sleep 2; ss -tlnp | grep 19996'),
    
    # Step 5: Start nftls client
    ('启动 nftls client', '/home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19996 -i "默认设备" -k 43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa -d 2>&1; sleep 3; ss -uln | grep 9996; ps -e | grep nftls'),
    
    # Step 6: Start tsensor
    ('启动 tsensor', 'systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor; ps -e | grep tsensor'),
    
    # Step 7: Wait for TLS connection
    ('等待TLS连接', 'timeout 15 bash -c "while ! cat /Agent/etc/nftls.status 2>/dev/null | grep -q online; do sleep 2; done"; cat /Agent/etc/nftls.status 2>/dev/null'),
]:
    print(f'\n=== {label} ===')
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:300]}')

# Final verification after chain restart
time.sleep(5)
for label, cmd in [
    ('最终进程状态', 'ps -e | grep -E "tsensor|nftls|fcapd|fsd|indexer" | head -10'),
    ('TLS状态', 'cat /Agent/etc/nftls.status 2>/dev/null'),
    ('端口', 'ss -tlnp | grep 19996; ss -uln | grep -E "999[56]"'),
    ('nfcapd current', 'ls -la /data/flow/1/nfcapd.current 2>/dev/null'),
]:
    print(f'\n=== {label} ===')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:300]}')
c.close()