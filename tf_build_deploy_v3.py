import paramiko, os, tarfile, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print('Creating tarball of ly_vis source (excluding node_modules, build, .git)...')

# Build the file list manually to handle Windows paths
src_base = r'd:\QorderProject\SOC\ly_vis'
dst_base = '/root/ly_vis_src'

tar_path = 'd:\\QorderProject\\SOC\\ly_vis_src.tar.gz'
with tarfile.open(tar_path, 'w:gz') as tar:
    for root, dirs, files in os.walk(src_base):
        # Skip excluded dirs
        rel = os.path.relpath(root, src_base).replace('\\', '/')
        if rel == '.':
            rel = ''
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'build', '.git')]

        for f in files:
            local_path = os.path.join(root, f)
            arcname = 'ly_vis_src/' + (rel + '/' + f if rel else f)
            tar.add(local_path, arcname=arcname)

print(f'Tarball created ({os.path.getsize(tar_path) / 1024 / 1024:.1f} MB)')

# Upload
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
print('Uploading...')
sftp.put(tar_path, '/root/ly_vis_src.tar.gz')
sftp.close()
print('Uploaded')

# Extract on server
i, o, e = c.exec_command('cd /root && rm -rf ly_vis_src && tar xzf ly_vis_src.tar.gz && ls ly_vis_src/ | head -5', timeout=60)
print('Extract:', o.read().decode()[:500])

# Yarn install (server already has node_modules cached, should be fast)
i, o, e = c.exec_command('cd /root/ly_vis_src && yarn install 2>&1 | tail -5', timeout=600)
print('Install:', o.read().decode()[:500])

# Build std package
i, o, e = c.exec_command('cd /root/ly_vis_src && yarn std build 2>&1 | tail -10', timeout=600)
print('Build:', o.read().decode()[:1000])

# Deploy
i, o, e = c.exec_command('cp -r /root/ly_vis_src/packages/std/build/* /Server/www/ui/; echo EX=$?', timeout=30)
print('Deploy:', o.read().decode()[:200])

i, o, e = c.exec_command('ls -la /Server/www/ui/ | head -5', timeout=30)
print('Verify:', o.read().decode()[:300])

c.close()
print('\nDone')