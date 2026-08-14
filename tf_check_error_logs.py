import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check apache error for actl on the most recent run
i, o, e = c.exec_command('tail -10 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:1000])

# Check if there are "no field" or "Error parsing" or "has no field" 
i, o, e = c.exec_command('grep -c "has no field\|Error parsing" /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Parse error count:', o.read().decode()[:100])

# Also check the system log for actl
i, o, e = c.exec_command('tail -10 /var/log/messages 2>/dev/null | grep -i "actl\|probe\|start_probe\|nftls" | tail -5', timeout=30)
print('System log:', o.read().decode()[:500])

c.close()