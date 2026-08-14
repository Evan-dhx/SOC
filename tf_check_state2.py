import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. BINARY FILES ===')
for cmd in [
    'ls -la /Agent/bin/actl 2>/dev/null',
    'ls -la /Agent/cmd/actl 2>/dev/null',
    'ls -la /Agent/bin/config_updater 2>/dev/null',
    'ls -la /Server/bin/config_pusher 2>/dev/null',
    'ls -la /Agent/lib/libcommon.so 2>/dev/null',
    'ls -la /Server/lib/libcommon.so 2>/dev/null',
]:
    i, o, e = c.exec_command(cmd, timeout=10)
    print(o.read().decode().strip())

print()
print('=== 2. ScriptAlias ===')
i, o, e = c.exec_command("grep ScriptAlias /etc/httpd/conf.d/*.conf", timeout=10)
print(o.read().decode().strip()[:2000])

print()
print('=== 3. config files ===')
i, o, e = c.exec_command('ls -la /Agent/data/config*', timeout=10)
print(o.read().decode().strip())

print()
print('=== 4. tsensor.conf ===')
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf', timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 5. actl HTTP test ===')
c.exec_command("cat > /tmp/check_actl.py << 'EOFSCRIPT'" + '\nimport urllib.request\nreq = urllib.request.Request("http://127.0.0.1:10081/actl",\n    data=b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: STATUS\\nid: \\"1\\"\\n",\n    method="POST")\ntry:\n    resp = urllib.request.urlopen(req, timeout=10)\n    print("HTTP:", resp.status)\nexcept Exception as ex:\n    print("ERROR:", str(ex)[:300])\nEOFSCRIPT', timeout=10)
time.sleep(1)
i, o, e = c.exec_command('python3 /tmp/check_actl.py 2>&1', timeout=30)
print(o.read().decode().strip())

print()
print('=== 6. Apache error log ===')
i, o, e = c.exec_command('tail -20 /var/log/httpd/ly_error_log 2>/dev/null', timeout=10)
print(o.read().decode().strip()[:1500])

print()
print('=== 7. tsensor processes ===')
i, o, e = c.exec_command('ps aux | grep -E "tsensor|probe" | grep -v grep', timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 8. config file content (first 50 lines) ===')
i, o, e = c.exec_command('head -50 /Agent/data/config 2>/dev/null', timeout=10)
print(o.read().decode().strip()[:2000])

c.close()