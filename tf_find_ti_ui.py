import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find the threat configuration dialog in the UI deployment
i, o, e = c.exec_command('grep -rn "threatconf\|api_key\|tic_host\|tisrs_host\|高级服务\|威胁情报服务" /Server/www/ui/ 2>/dev/null | head -20', timeout=30)
print(o.read().decode()[:2000])

c.close()