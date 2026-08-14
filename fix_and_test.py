import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Fix config: use BOTH password= (for MySQL) and passwd= (for app code)
    ("fix config both", r"""
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[client]
user=root
password=password123

[gl.server]
user=root
password=password123
passwd=password123
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # Test mysql client
    ("test mysql", r"""
mysql -u root -p'password123' -e "SELECT 'MySQL OK' AS status;" 2>&1
"""),
    
    # Create tables
    ("create tables", r"""
mysql -u root -p'password123' server << 'EOSQL'
CREATE TABLE IF NOT EXISTS \`t_user\` (
  \`id\` int(11) NOT NULL AUTO_INCREMENT,
  \`name\` varchar(64) NOT NULL,
  \`pass\` varchar(128) NOT NULL,
  \`level\` varchar(32) DEFAULT 'viewer',
  \`resource\` varchar(256) DEFAULT '*',
  \`disabled\` char(1) DEFAULT 'N',
  \`lockedtime\` int(11) DEFAULT 0,
  \`lasttime\` int(11) DEFAULT 0,
  \`lastip\` varchar(64) DEFAULT '',
  \`lastsession\` varchar(64) DEFAULT '',
  PRIMARY KEY (\`id\`),
  UNIQUE KEY \`name\` (\`name\`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS \`t_user_session\` (
  \`sid\` varchar(64) NOT NULL,
  \`uid\` int(11) NOT NULL,
  \`expire_time\` bigint(20) NOT NULL,
  PRIMARY KEY (\`sid\`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS \`t_user_session_history\` (
  \`sid\` varchar(64) NOT NULL,
  \`uid\` int(11) NOT NULL,
  \`action\` varchar(64) NOT NULL,
  \`code\` int(11) NOT NULL,
  \`time\` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO \`t_user\` (\`name\`, \`pass\`, \`level\`, \`resource\`) 
VALUES ('admin', MD5('admin'), 'sysadmin', '*')
ON DUPLICATE KEY UPDATE \`name\`=\`name\`;

SHOW TABLES;
EOSQL
"""),
    
    # Test CGI
    ("test CGI", r"""
curl -s http://localhost/d/auth 2>&1
echo ""
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
"""),
    
    # Check latest error log
    ("latest error", "tail -5 /var/log/httpd/ly_error_log"),
    
    # Check debug log from PrivateTmp
    ("debug log", r"""
find /tmp/systemd-private-*httpd*/tmp/ -name '*.log' 2>/dev/null -exec cat {} \;
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
