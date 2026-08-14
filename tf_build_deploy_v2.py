import paramiko, os, tarfile, sys
from io import BytesIO
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TARBALL = 'd:\\QorderProject\\SOC\\ly_vis_src.tar.gz'

# Create tarball of only source files (not node_modules)
def filter_tarinfo(ti):
    name = ti.name.replace('\\', '/')
    # Exclude node_modules, build, .git
    if '/node_modules/' in name or name == 'node_modules':
        return None
    if '/build/' in name or name == 'build':
        return None
    if '/.git/' in name or name == '.git':
        return None
    if name.startswith('ly_vis/') or name.startswith('ly_vis\\'):
        return ti
    return None

print('Creating tarball of ly_vis source...')
with tarfile.open(TARBALL, 'w:gz') as tar:
    tar.add(r'd:\QorderProject\SOC\ly_vis', arcname='ly_vis_src', filter=filter_tarinfo)
print(f'Tarball created ({os.path.getsize(TARBALL) / 1024 / 1024:.1f} MB)')

# Upload to server
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()

print('Uploading tarball to server...')
sftp.put(TARBALL, '/root/ly_vis_src.tar.gz')
sftp.close()
print('Uploaded')

# Extract on server
i, o, e = c.exec_command('cd /root && rm -rf ly_vis_src && tar xzf ly_vis_src.tar.gz && ls ly_vis_src/', timeout=60)
print('Extracted:', o.read().decode()[:300])

# Fix SSL for yarn on server
i, o, e = c.exec_command('yarn config set strict-ssl false -g 2>&1; yarn config get strict-ssl 2>&1', timeout=30)
print('Yarn SSL:', o.read().decode()[:200])

# Install
i, o, e = c.exec_command('cd /root/ly_vis_src && yarn install 2>&1 | tail -10', timeout=600)
print('Install:', o.read().decode()[:500])

# Build
i, o, e = c.exec_command('cd /root/ly_vis_src && npm run std build 2>&1 | tail -20', timeout=600)
print('Build:', o.read().decode()[:1000])

# Deploy
i, o, e = c.exec_command('cp -r /root/ly_vis_src/packages/std/build/* /Server/www/ui/ 2>&1; echo EX=$?', timeout=30)
print('Deploy:', o.read().decode()[:200])

i, o, e = c.exec_command('ls -la /Server/www/ui/ | head -5', timeout=30)
print('Verify:', o.read().decode()[:300])

c.close()
print('\n=== Done ===')