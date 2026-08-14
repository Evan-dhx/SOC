import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Create the "server" database (code expects this name)
    ("create server db", r"""
mysql -u root -p'PP@ssw0rd' -e "CREATE DATABASE IF NOT EXISTS \`server\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1
echo "Exit: $?"
"""),
    
    # 2. Create the config file with password
    ("create db conf", r"""
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[gl.server]
passwd=PP@ssw0rd
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Config created:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # 3. Test DB connection with cppdb-style params
    ("test db connect", r"""
mysql -u root -p'PP@ssw0rd' server -e "SELECT 'DB connection OK' AS status;" 2>&1
"""),
    
    # 4. Test CGI auth endpoint
    ("test auth CGI", r"""
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost/d/auth
echo ""
curl -s http://localhost/d/auth 2>&1 | head -5
"""),
    
    # 5. Check error log
    ("error log", "tail -10 /var/log/httpd/ly_error_log 2>/dev/null"),
    
    # 6. Check if tables exist (they might not yet)
    ("check tables", r"""
mysql -u root -p'PP@ssw0rd' server -e "SHOW TABLES;" 2>&1
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
