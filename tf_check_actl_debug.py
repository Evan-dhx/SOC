import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check log for CachedConfig parse result
i, o, e = c.exec_command('tail -10 /var/log/messages 2>/dev/null | grep -E "actl|CachedConfig|config|Failed"', timeout=30)
print('Recent log:', o.read().decode()[:500])

# Check apache error log for actl errors
i, o, e = c.exec_command('tail -5 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:500])

# Run actl STATUS with debug
i, o, e = c.exec_command(r"printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\ndbg: \"ALL\"\n' > /tmp/actl_dbg.txt && curl -s -w '\nHTTP:%{http_code}' -X POST -d @/tmp/actl_dbg.txt 'http://127.0.0.1:10081/actl?dbg=1' 2>&1 | head -20", timeout=30)
print('actl with debug:', o.read().decode()[:500])

c.close()