import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Download the index.html
sftp = c.open_sftp()
sftp.get('/Server/www/ui/index.html', 'd:\\QorderProject\\SOC\\index.html.bak')
sftp.close()
print('Downloaded index.html')

# Check the relevant lines
with open('d:\\QorderProject\\SOC\\index.html.bak', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the relevant section
idx = content.find('高级服务 API_KEY')
if idx >= 0:
    # Show context
    start = max(0, idx - 200)
    end = min(len(content), idx + 200)
    print(f'Found at position {idx}')
    print(content[start:end])
else:
    print('Not found')
c.close()