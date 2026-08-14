import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Update config file with new password
    ("update db conf", r"""
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[gl.server]
passwd=password123
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Updated config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # 2. Test auth as apache user
    ("test as apache", r"""
su -s /bin/bash apache -c "/Server/www/d/auth" 2>&1 | head -5
"""),
    
    # 3. Test CGI via curl
    ("test CGI", r"""
curl -s http://localhost/d/auth 2>&1 | head -10
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
"""),
    
    # 4. If still failing, the issue is socket vs TCP
    # Let's check what happens
    ("check error", "tail -5 /var/log/httpd/ly_error_log"),
    
    # 5. If socket auth fails, configure MariaDB to allow socket auth with password
    ("fix socket auth", r"""
# The issue: cppdb connects via unix socket as 'apache' user
# MariaDB might need unix_socket plugin or we need to allow password over socket
# Let's try: grant root@localhost with mysql_native_password explicitly
mysql -u root -p'password123' << 'EOSQL'
-- Ensure password auth works over socket
SET GLOBAL unix_socket_auth = OFF;
-- Or use a different approach: create user for apache
CREATE USER IF NOT EXISTS 'ly_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON \`server\`.* TO 'ly_user'@'localhost';
GRANT ALL PRIVILEGES ON \`ly_server\`.* TO 'ly_user'@'localhost';
GRANT ALL PRIVILEGES ON \`ly_agent\`.* TO 'ly_user'@'localhost';
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user;
EOSQL
"""),
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
