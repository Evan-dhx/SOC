import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Fix the device insert (no status column)
    ("fix device insert", r"""
mysql -u root -p'password123' server << 'EOSQL'
INSERT INTO `t_agent` (`id`, `name`, `ip`, `status`) VALUES
(1, '默认分析节点', '127.0.0.1', 'active')
ON DUPLICATE KEY UPDATE `name`=`name`;

INSERT INTO `t_device` (`id`, `name`, `type`, `agentid`, `ip`) VALUES
(1, '默认设备', 'netflow', 1, '127.0.0.1')
ON DUPLICATE KEY UPDATE `name`=`name`;

SELECT 'Default data inserted' AS status;
EOSQL
"""),
    
    # Verify all tables exist
    ("verify tables", r"""
mysql -u root -p'password123' server -e "SHOW TABLES;" 2>&1
"""),
    
    # Test all endpoints
    ("test all endpoints", r"""
echo "=== auth (login) ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin"
echo ""
echo "=== config ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/config
echo ""
echo "=== event ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/event
echo ""
echo "=== feature ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/feature
echo ""
echo "=== bwlist ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/bwlist
echo ""
echo "=== mo ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/mo
echo ""
echo "=== internalip ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/internalip
echo ""
"""),
    
    # Check error log for any remaining issues
    ("check errors", r"""
tail -5 /var/log/httpd/ly_error_log
"""),
    
    # Test from browser's perspective - login then access overview
    ("browser flow test", r"""
# Login and get session cookie
COOKIE=$(curl -s -D - http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" 2>/dev/null | grep 'Set-Cookie' | sed 's/.*SESSION_ID=\([^;]*\).*/\1/')
echo "Session: $COOKIE"

# Use session to access config
echo "Config with session:"
curl -s -o /dev/null -w "%{http_code}" -b "SESSION_ID=$COOKIE" http://localhost/d/config
echo ""

# Access event
echo "Event with session:"
curl -s -o /dev/null -w "%{http_code}" -b "SESSION_ID=$COOKIE" http://localhost/d/event
echo ""
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
