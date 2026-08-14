import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Fix the placeholder text
with open('d:\\QorderProject\\SOC\\index.html.bak', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the placeholders to match user's expected config file references
old_placeholders = {
    'placeholder="威胁情报服务 KEY"': 'placeholder="tisrs.conf 中的 KEY"',
    'placeholder="HOST，如 10.0.0.1"': 'placeholder="tisrs.conf 中的 HOST，如 10.0.0.1"',
    'placeholder="PORT，如 8080"': 'placeholder="tisrs.conf 中的 PORT，如 8080"',
    'placeholder="高级服务 API_KEY"': 'placeholder="tic.conf 中的 API_KEY"',
    'placeholder="HOST"': 'placeholder="tic.conf 中的 HOST"',
    'placeholder="PORT"': 'placeholder="tic.conf 中的 PORT"',
}

for old, new in old_placeholders.items():
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {old} -> {new}')
    else:
        print(f'Not found: {old}')

# Save locally
with open('d:\\QorderProject\\SOC\\index.html.fixed', 'w', encoding='utf-8') as f:
    f.write(content)

print('\nFixed file saved locally')

# Upload to server and backup original
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = c.open_sftp()
# Backup original
i, o, e = c.exec_command('cp /Server/www/ui/index.html /Server/www/ui/index.html.bak.$(date +%s)', timeout=30)
print('Backup:', o.read().decode()[:100])

# Upload fixed
sftp.put('d:\\QorderProject\\SOC\\index.html.fixed', '/Server/www/ui/index.html')
sftp.close()
print('Uploaded fixed index.html')

# Verify
i, o, e = c.exec_command('grep "tic.conf\\|tisrs.conf" /Server/www/ui/index.html', timeout=30)
print('Verify:', o.read().decode()[:600])

c.close()

import os
os.remove('d:\\QorderProject\\SOC\\index.html.bak')
os.remove('d:\\QorderProject\\SOC\\index.html.fixed')
print('Temp files cleaned')