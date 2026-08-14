import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the deployed JS for our fix pattern
# Look for the modal-device related code - check if tls_psk mapping exists
i, o, e = c.exec_command(r'ls -la /Server/www/ui/static/js/', timeout=30)
print('JS files:', o.read().decode()[:500])

# Grep for "tls_psk" in all JS files
i, o, e = c.exec_command(r'grep -l "tls_psk\|delete.*tls_status\|delete.*tls_last" /Server/www/ui/static/js/*.js 2>/dev/null', timeout=30)
print('Files with fix:', o.read().decode()[:500])

# Also check for the psk mapping pattern
i, o, e = c.exec_command(r'grep -oa "psk.*tls_psk\|tls_psk.*psk" /Server/www/ui/static/js/*.chunk.js 2>/dev/null | head -5', timeout=30)
print('PSK mapping:', o.read().decode()[:300])

# Check if the old behavior (raw field display) is still there
i, o, e = c.exec_command(r'grep -c "tls_status\|tls_last_seen" /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null', timeout=30)
print('Raw field counts:', o.read().decode()[:300])

c.close()