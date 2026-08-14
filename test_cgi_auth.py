import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Test auth CGI again after DB fix
    ("test auth now", r"""
curl -s http://localhost/d/auth 2>&1 | head -10
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
"""),
    
    # Check the latest error log
    ("latest error", "tail -5 /var/log/httpd/ly_error_log"),
    
    # Test if cppdb can connect - check if the issue is socket vs TCP
    # cppdb with localhost uses socket, let's see if we need to force TCP
    ("cppdb test", r"""
# Try running auth binary directly as apache user to see exact error
su -s /bin/bash apache -c "/Server/www/d/auth" 2>&1 | head -5
"""),
    
    # Check if there's a way to force TCP in cppdb
    # The connection string uses "mysql:database=server;..." 
    # cppdb mysql backend might support host=127.0.0.1
    ("check cppdb conn", r"""
# Let's see what connection string the binary actually uses
strings /Server/www/d/auth | grep -E 'server|gl\.server|read_default|database=' | head -10
"""),
    
    # The issue might be that cppdb connects via socket and MariaDB
    # needs password auth for socket connections too
    # Let's check if mysql client from apache user works with -h 127.0.0.1
    ("apache TCP test", r"""
su -s /bin/bash apache -c "mysql -u root -p'PP@ssw0rd' -h 127.0.0.1 -e 'SELECT 1;'" 2>&1
"""),
    
    # Check if the problem is the @ in password for cppdb parsing
    ("check password", r"""
# Test with a simpler password to rule out @ issue
mysql -u root -p'PP@ssw0rd' -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'password123'; FLUSH PRIVILEGES;" 2>&1
echo "Password changed"
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
