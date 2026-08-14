import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check full error log
    ("full error log", "tail -20 /var/log/httpd/ly_error_log"),
    
    # Check if server database has tables
    ("check tables", r"""
mysql -u root -p'password123' server -e "SHOW TABLES;" 2>&1
"""),
    
    # Run auth binary directly with CGI env vars
    ("run auth directly", r"""
SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 /Server/www/d/auth 2>&1 | head -10
"""),
    
    # Check if the issue is missing tables - create basic schema
    ("create tables", r"""
mysql -u root -p'password123' server << 'EOSQL'
-- Create basic tables needed by the auth CGI
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

-- Create default admin user (password: admin)
INSERT INTO \`t_user\` (\`name\`, \`pass\`, \`level\`, \`resource\`) 
VALUES ('admin', MD5('admin'), 'sysadmin', '*')
ON DUPLICATE KEY UPDATE \`name\`=\`name\`;

SELECT 'Tables created' AS status;
SHOW TABLES;
EOSQL
"""),
    
    # Test again
    ("test again", r"""
curl -s http://localhost/d/auth 2>&1
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
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
