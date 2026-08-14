import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Write correct config with psk
i, o, e = c.exec_command(r"""cat > /Agent/data/config << 'EOFCFG'
controller { host: "127.0.0.1" port: "10081" }
dev {
  id: 1 name: "默认设备" type: "netflow" model: "" agentid: 1
  ip: "127.0.0.1" port: 9995 disabled: false flowtype: "netflow"
  pcap_level: 0 temp: "V9,IPV4" filter: "" interface: "ens192"
  psk: "43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa"
}
EOFCFG
rm -f /Agent/data/config.tmp
grep "psk:" /Agent/data/config
wc -c /Agent/data/config""", timeout=30)
print('Config:', o.read().decode()[:300])

# Step 2: Write correct psk file
i, o, e = c.exec_command('echo "默认设备:43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa" > /Agent/etc/nftls.psk; chmod 600 /Agent/etc/nftls.psk; wc -c /Agent/etc/nftls.psk', timeout=30)
print('PSK file:', o.read().decode()[:200])

# Step 3: Kill old nftls and start fresh with correct psk
i, o, e = c.exec_command('pkill nftls 2>/dev/null; sleep 2; ps -e | grep -c nftls', timeout=30)
print('Killed nftls:', o.read().decode()[:100])

time.sleep(2)

# Start nftls server via /Agent/bin/nftls (full path already)
i, o, e = c.exec_command('/home/Agent/bin/nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /Agent/etc/nftls.status -d 2>&1; sleep 2; ss -tlnp | grep 19996', timeout=30)
print('nftls server:', o.read().decode()[:200])

# Start nftls client
i, o, e = c.exec_command('/home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19996 -i "默认设备" -k 43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa -d 2>&1; sleep 2; ps -e | grep nftls | head -3', timeout=30)
print('nftls client:', o.read().decode()[:200])

# Start nfcapd
i, o, e = c.exec_command('pkill -9 nfcapd 2>/dev/null; sleep 1; mkdir -p /Agent/flow/1; /Agent/bin/nfcapd -w -D -p 9995 -l /Agent/flow/1 -z -b 0.0.0.0 2>&1; sleep 2; ps -e | grep fcapd', timeout=30)
print('nfcapd:', o.read().decode()[:200])

# Start tsensor
i, o, e = c.exec_command('systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor', timeout=30)
print('tsensor:', o.read().decode()[:100])

# Wait for TLS connection
time.sleep(10)
i, o, e = c.exec_command('cat /Agent/etc/nftls.status 2>/dev/null', timeout=30)
print('TLS status:', o.read().decode()[:300])

c.close()

print('\n=== 基础链路已恢复 ===')