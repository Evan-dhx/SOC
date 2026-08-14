import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Step 1: Fix config file with minimal valid content
    '''cat > /Agent/data/config << 'ENDOFFILE'
controller {
  host: "127.0.0.1"
  port: "10081"
}
ENDOFFILE
echo "restored config: $(wc -c < /Agent/data/config) bytes"''',
    
    # Step 2: Test POST with a simple dev config via curl
    '''curl -sv -X POST \\
  -d 'controller { host: "127.0.0.1" port: "10081" } dev { id: 1 name: "test" psk: "abc123" }' \\
  http://127.0.0.1:10081/config_updater 2>&1 |
  head -30''',
    
    # Step 3: Check config file after curl POST
    'echo "=== config after curl ==="; cat /Agent/data/config; echo; wc -c /Agent/data/config',
    
    # Step 4: Now run production pusher again
    '/home/Server/bin/config_pusher > /tmp/pusher2.log 2>&1; echo "PUSHER_EXIT=$?"',
    
    # Step 5: Check config after pusher
    'echo "=== config after pusher ==="; cat /Agent/data/config; echo; wc -c /Agent/data/config',
    
    # Step 6: Check pusher log for any output
    'cat /tmp/pusher2.log; echo "---"; wc -c /tmp/pusher2.log',
    
    # Step 7: Check status log for errors
    'tail -5 /Agent/data/log',
]
for label, cmd in cmds:
    print(f'\n[{label}]')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
    time.sleep(0.5)
client.close()