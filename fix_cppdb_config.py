import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # The cppdb mysql backend reads password from MySQL config files
    # NOT from the connection string's password= parameter
    # The code reads passwd from DB_CONF but cppdb ignores it
    # Solution: put credentials in the MySQL config that cppdb reads
    
    # 1. Create proper MySQL config for the gl.server group
    ("create mysql config", r"""
# cppdb reads from standard MySQL config locations
# The read_default_group=gl.server means it looks for [gl.server] in my.cnf files
# Put the credentials there
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[gl.server]
user=root
password=password123
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # 2. Also keep the passwd= line for the application code
    ("add passwd line", r"""
# The app code reads 'passwd=' from this file too
# Append it
echo 'passwd=password123' >> /etc/my.cnf.d/gl.server.cnf
echo "Final config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # 3. Test
    ("test auth", r"""
su -s /bin/bash apache -c "/Server/www/d/auth" 2>&1 | head -5
"""),
    
    # 4. Test CGI
    ("test CGI", r"""
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
curl -s http://localhost/d/auth 2>&1 | head -3
"""),
    
    # 5. Check error log
    ("error log", "tail -5 /var/log/httpd/ly_error_log"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
