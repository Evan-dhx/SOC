import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restart tsensor manually via systemd
i, o, e = c.exec_command('systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor; echo ---; ps -e | grep tsensor', timeout=30)
print('systemctl restart:', o.read().decode()[:500])

# Check tsensor config
i, o, e = c.exec_command("cat /proc/$(pidof tsensor)/cmdline 2>/dev/null | tr '\\0' ' '", timeout=30)
print('New tsensor cmd:', o.read().decode()[:300])

c.close()