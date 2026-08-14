import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Remove old chunk files to prevent caching confusion
i, o, e = c.exec_command(r'cd /Server/www/ui/static/js && ls *.chunk.js', timeout=30)
chunks = o.read().decode().strip().split('\n')
print('All chunk files:', chunks)

# Keep only the newest ones (based on timestamp/name)
# The new build creates main.5d1e7c0d.chunk.js and 2.a4d466e2.chunk.js
# Old ones are main.ff156c89.chunk.js and 2.2db6edf7.chunk.js
i, o, e = c.exec_command(r'rm -f /Server/www/ui/static/js/main.ff156c89.chunk.js /Server/www/ui/static/js/main.ff156c89.chunk.js.map 2>/dev/null; echo done', timeout=30)
print('Cleanup old:', o.read().decode()[:100])

# Verify index.html references the new JS
i, o, e = c.exec_command(r'grep -o "main\.[a-z0-9]*\.chunk\.js" /Server/www/ui/index.html', timeout=30)
print('Index references:', o.read().decode()[:200])

c.close()