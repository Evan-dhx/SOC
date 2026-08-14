import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    # Step 1: Write config file with full content directly (bypass config_updater)
    ("write full config with psk", r"""cat > /Agent/data/config << 'EOFCFG'
controller {
  host: "127.0.0.1"
  port: "10081"
}
dev {
  id: 1
  name: "\351\273\230\350\256\244\350\256\276\345\244\207"
  type: "netflow"
  model: ""
  agentid: 1
  ip: "127.0.0.1"
  port: 0
  disabled: false
  flowtype: "netflow"
  pcap_level: 0
  temp: ""
  filter: ""
  interface: ""
  psk: "43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa"
}
EOFCFG
echo "written: $(wc -c < /Agent/data/config) bytes"
head -5 /Agent/data/config"""),
    
    # Step 2: Verify config via config_updater GET
    ('config_updater GET', 'REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null | head -20'),
    
    # Step 3: Check if fsd picks it up
    ('fsd status', 'ss -tlnp 2>/dev/null | grep -E "1999[56]" ; ps aux | grep nftls | grep -v grep ; cat /Agent/etc/nftls.psk 2>/dev/null | sed "s/:.*/:***/"'),
    
    # Step 4: Check log for any nftls related messages
    ('tail log', 'tail -10 /Agent/data/log'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()