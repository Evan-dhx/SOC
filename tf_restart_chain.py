import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Write psk file
i,o,e = c.exec_command('echo "默认设备:43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa" > /Agent/etc/nftls.psk; chmod 600 /Agent/etc/nftls.psk; wc -c /Agent/etc/nftls.psk', timeout=30)
print('psk file:', o.read().decode()[:200])

# Step 2: Kill old nftls
i,o,e = c.exec_command('pkill nftls 2>/dev/null; sleep 2', timeout=30)
print('killed old nftls')

# Step 3: Restart nftls server
i,o,e = c.exec_command('/home/Agent/bin/nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /Agent/etc/nftls.status -d 2>&1; sleep 2; ss -tlnp | grep 19996', timeout=30)
print('server:', o.read().decode()[:200])

# Step 4: Start nftls client
i,o,e = c.exec_command('/home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19996 -i "默认设备" -k 43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa -d 2>&1; sleep 3', timeout=30)
print('client started')

# Step 5: Restart tsensor
i,o,e = c.exec_command('systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor', timeout=30)
print('tsensor:', o.read().decode()[:200])

# Step 6: Wait and check
time.sleep(10)
i,o,e = c.exec_command('cat /Agent/etc/nftls.status 2>/dev/null; echo; ps -e | grep -c nftls; ps -e | grep tsensor | grep -v grep | head -2', timeout=30)
print('status:', o.read().decode()[:500])

# Step 7: Check data flow
i,o,e = c.exec_command('ls -la /data/flow/1/nfcapd.current 2>/dev/null; ss -uln | grep 9996; ss -uln | grep 9995', timeout=30)
print('flow:', o.read().decode()[:500])

c.close()