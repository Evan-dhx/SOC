import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check MariaDB auth plugin for root
    ("root auth plugin", r"""
mysql -u root -p'PP@ssw0rd' -e "SELECT user, host, plugin FROM mysql.user WHERE user='root';" 2>&1
"""),
    
    # Check if unix_socket plugin is used (common in AlmaLinux)
    ("mariadb version", "mariadb --version 2>&1"),
    
    # Try connecting as apache user (how CGI runs)
    ("test as apache", r"""
su -s /bin/bash apache -c "mysql -u root -p'PP@ssw0rd' -e 'SELECT 1;'" 2>&1
"""),
    
    # Check MariaDB socket
    ("mariadb socket", r"""
mysql -u root -p'PP@ssw0rd' -e "SHOW VARIABLES LIKE 'socket';" 2>&1
ls -la /var/lib/mysql/mysql.sock 2>/dev/null
ls -la /var/run/mariadb/mariadb.sock 2>/dev/null
"""),
    
    # Create a dedicated user for the app
    ("create app user", r"""
mysql -u root -p'PP@ssw0rd' << 'EOSQL'
-- Create user that can connect from localhost
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'PP@ssw0rd';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;

-- Also ensure root@localhost works with password
ALTER USER 'root'@'localhost' IDENTIFIED BY 'PP@ssw0rd';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;

FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
EOSQL
"""),
    
    # Test connection via 127.0.0.1 (TCP) vs localhost (socket)
    ("test TCP connect", r"""
mysql -u root -p'PP@ssw0rd' -h 127.0.0.1 -e "SELECT 'TCP OK' AS status;" 2>&1
echo "---"
mysql -u root -p'PP@ssw0rd' -h localhost -e "SELECT 'Socket OK' AS status;" 2>&1
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
