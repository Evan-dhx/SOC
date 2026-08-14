import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check package.json for build script
i, o, e = c.exec_command('cd /root/ly_vis_src/packages/std && cat package.json | grep -A5 "\"build\""', timeout=30)
print('Build script:', o.read().decode()[:500])

# Try building directly
i, o, e = c.exec_command('cd /root/ly_vis_src/packages/std && npx react-app-rewired build 2>&1 | tail -30', timeout=600)
print('Rebuild:', o.read().decode()[:2000])

c.close()