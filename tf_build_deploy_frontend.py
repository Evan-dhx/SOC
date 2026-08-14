import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()

# 1. Create ly_vis source dir on server
i, o, e = c.exec_command('mkdir -p /root/SOC/ly_vis_src/packages/components/ui/modal/modal-device', timeout=30)
print('mkdir:', o.read().decode()[:100])

# 2. Upload the modified modal-device/index.jsx
local = r'd:\QorderProject\SOC\ly_vis\packages\components\ui\modal\modal-device\index.jsx'
remote = '/root/SOC/ly_vis_src/packages/components/ui/modal/modal-device/index.jsx'
sftp.put(local, remote)
print('Uploaded modal-device/index.jsx')

# 3. Also upload the rest of the ui/form components (needed for PskInput)
src_base = r'd:\QorderProject\SOC\ly_vis\packages\components\ui'
dst_base = '/root/SOC/ly_vis_src/packages/components/ui'
for root, dirs, files in os.walk(src_base):
    for f in files:
        if f.endswith('.jsx') or f.endswith('.js') or f.endswith('.less') or f.endswith('.css') or f.endswith('.json'):
            local_path = os.path.join(root, f)
            rel = os.path.relpath(local_path, src_base)
            remote_path = dst_base + '/' + rel.replace('\\', '/')
            remote_dir = os.path.dirname(remote_path)
            c.exec_command(f'mkdir -p {remote_dir}', timeout=10)
            sftp.put(local_path, remote_path)
print('Uploaded ui components')

# 4. Upload std package files (service, utils, etc.)
for sub in ['service', 'utils', 'page']:
    src = rf'd:\QorderProject\SOC\ly_vis\packages\std\src\{sub}'
    dst = f'/root/SOC/ly_vis_src/packages/std/src/{sub}'
    if os.path.isdir(src):
        for root, dirs, files in os.walk(src):
            for f in files:
                if f.endswith('.jsx') or f.endswith('.js'):
                    local_path = os.path.join(root, f)
                    rel = os.path.relpath(local_path, src)
                    remote_path = f'{dst}/{rel}'
                    c.exec_command(f'mkdir -p {os.path.dirname(remote_path)}', timeout=10)
                    sftp.put(local_path, remote_path)

# 5. Upload package.json and config files
for f in ['package.json', 'lerna.json', '.eslintrc.js', '.prettierrc.js', 'yarn.lock']:
    local_path = rf'd:\QorderProject\SOC\ly_vis\{f}'
    if os.path.isfile(local_path):
        sftp.put(local_path, f'/root/SOC/ly_vis_src/{f}')
        print(f'Uploaded {f}')

sftp.close()

# 6. Install dependencies and build on server
i, o, e = c.exec_command('cd /root/SOC/ly_vis_src && yarn install --frozen-lockfile 2>&1 | tail -20', timeout=600)
print('yarn install:', o.read().decode()[:500])

i, o, e = c.exec_command('cd /root/SOC/ly_vis_src && npm run std build 2>&1 | tail -20', timeout=600)
print('build:', o.read().decode()[:500])

# 7. Deploy to www
i, o, e = c.exec_command('cp -r /root/SOC/ly_vis_src/packages/std/build/* /Server/www/ui/ 2>&1', timeout=30)
print('Deploy:', o.read().decode()[:200])

i, o, e = c.exec_command('ls -la /Server/www/ui/ | head -5', timeout=30)
print('Verify:', o.read().decode()[:300])

c.close()
print('\n=== Done ===')