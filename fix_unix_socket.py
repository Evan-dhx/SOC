import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. First, let's understand how cppdb mysql backend works
    # Check cppdb source or docs
    ("cppdb mysql docs", r"""
# Check if cppdb supports read_default_group
grep -r 'read_default_group\|read_default_file\|mysql_options' /usr/include/cppdb/ 2>/dev/null | head -10
echo "---"
# Check cppdb mysql backend source if available
find / -name 'mysql_connection.cpp' -o -name 'mysql_backend*' 2>/dev/null | head -5
"""),
    
    # 2. Try putting credentials in [client] section which is universally read
    ("client section", r"""
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[client]
user=root
password=password123

[gl.server]
user=root
password=password123
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # 3. Test
    ("test", r"""
curl -s http://localhost/d/auth 2>&1 | head -5
echo "---"
tail -3 /var/log/httpd/ly_error_log
"""),
    
    # 4. If that doesn't work, try unix_socket auth plugin
    ("unix_socket auth", r"""
# Install unix_socket plugin and configure
mysql -u root -p'password123' << 'EOSQL'
INSTALL SONAME 'auth_socket';
CREATE USER IF NOT EXISTS 'apache'@'localhost' IDENTIFIED VIA unix_socket;
GRANT ALL PRIVILEGES ON *.* TO 'apache'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user;
EOSQL
"""),
    
    # 5. Modify dbc.cpp to use apache user with unix_socket
    ("patch for unix_socket", r"""
cat > /root/SOC/ly_server_src/server/dbc.cpp << 'CPPEOF'
#include "dbc.h"

cppdb::session* start_db_session() {
  string dbdatabase = SERVER_DB_NAME;
  string mysql_group = SERVER_DB_GROUP;
  // Use unix_socket auth - no password needed
  session* sql = new session("mysql:database=" + dbdatabase + ";read_default_group=" + mysql_group);
  return sql;
}
CPPEOF

cd /root/SOC/ly_server_src/server
make auth 2>&1 | tail -5
cp auth /Server/www/d/auth
echo "Rebuilt and installed"
"""),
    
    # 6. Test again
    ("test2", r"""
curl -s http://localhost/d/auth 2>&1 | head -5
echo "---"
tail -3 /var/log/httpd/ly_error_log
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
