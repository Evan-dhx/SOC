import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    # Check what protobuf libs config_updater and config_pusher use
    ('config_updater ldd protobuf', 'ldd /home/Agent/cmd/config_updater 2>/dev/null | grep -i proto'),
    ('config_pusher ldd protobuf', 'ldd /home/Server/bin/config_pusher 2>/dev/null | grep -i proto'),
    
    # Check actual test post content
    ('test post content hex', 'cat /tmp/test_post.txt | xxd | head -5; echo; echo "TEXT:"; cat /tmp/test_post.txt'),
    
    # Try POST with explicit Content-Type text/plain
    ('curl with text/plain', "curl -s -X POST -H 'Content-Type: text/plain' -d 'controller { host: \"127.0.0.1\" port: \"10081\" } dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?"),
    
    ('config after text/plain', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
    
    # Restore config and try with content-type application/octet-stream
    ("restore config", "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; echo restored"),
    
    ('curl with octet-stream', "curl -s -X POST -H 'Content-Type: application/octet-stream' -d 'controller { host: \"127.0.0.1\" port: \"10081\" } dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?"),
    
    ('config after octet-stream', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
    
    # Test with simple config with no IP (no dots that look like numbers)
    ("restore config again", "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; echo restored"),
    
    ('curl with simple data', "curl -s -X POST -H 'Content-Type: text/plain' -d 'dev { id:1 name:\"test\" psk:\"abc\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?"),
    
    ('config after simple', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()