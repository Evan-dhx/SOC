import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check if psk descriptors are in the new libcommon.so
i, o, e = c.exec_command('strings /lib64/libcommon.so | grep -c "psk"', timeout=30)
print('psk count in libcommon.so:', o.read().decode()[:100])

# Check if the error is STILL happening
i, o, e = c.exec_command(r"printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\n' > /tmp/actl_t.txt && curl -s -w '\nHTTP:%{http_code}' -X POST -d @/tmp/actl_t.txt http://127.0.0.1:10081/actl 2>&1 | head -5", timeout=30)
print('actl STATUS:', o.read().decode()[:300])

# Check the error log
i, o, e = c.exec_command('tail -3 /var/log/httpd/ly_error_log 2>/dev/null | grep -o "has no field\|psk\|Error parsing" | head -3', timeout=30)
print('Latest error:', o.read().decode()[:200])

c.close()