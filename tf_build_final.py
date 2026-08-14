import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Build with NODE_OPTIONS for OpenSSL compatibility
i, o, e = c.exec_command('cd /root/ly_vis_src/packages/std && NODE_OPTIONS=--openssl-legacy-provider npx react-app-rewired build 2>&1 | tail -10', timeout=600)
print('Build:', o.read().decode()[:2000])

# Deploy if build succeeded
i, o, e = c.exec_command('ls /root/ly_vis_src/packages/std/build/static/js/main.*.js 2>/dev/null && echo EXISTS || echo FAIL', timeout=30)
print('Check:', o.read().decode()[:100])

i, o, e = c.exec_command('cp -r /root/ly_vis_src/packages/std/build/* /Server/www/ui/; echo EX=$?', timeout=30)
print('Deploy:', o.read().decode()[:100])

# Verify the fix is in the deployed JS
i, o, e = c.exec_command('grep -c "tls_psk\|tls_last_seen\|tls_status" /Server/www/ui/static/js/main.*.js', timeout=30)
print('JS grep (should be >0 for tls_psk formatTimestamp):', o.read().decode()[:200])

i, o, e = c.exec_command('grep "processedInitialValues\|useMemo" /Server/www/ui/static/js/main.*.js | head -3', timeout=30)
print('Fix confirmed:', o.read().decode()[:300])

c.close()
print('\nDone')