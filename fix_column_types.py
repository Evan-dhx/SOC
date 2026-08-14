import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_event_action: act should be int (uint32 in proto)
ALTER TABLE `t_event_action` MODIFY COLUMN `act` int(11) DEFAULT 0;
ALTER TABLE `t_event_action` MODIFY COLUMN `uid` int(11) DEFAULT 0;

-- Fix t_event_ignore: time should be int (uint32 in proto)
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` int(11) DEFAULT 0;
ALTER TABLE `t_event_ignore` MODIFY COLUMN `tport` int(11) DEFAULT 0;
ALTER TABLE `t_event_ignore` MODIFY COLUMN `count` int(11) DEFAULT 0;

-- Also fix t_blacklist and t_whitelist: time should be int
ALTER TABLE `t_blacklist` MODIFY COLUMN `time` int(11) DEFAULT 0;
ALTER TABLE `t_whitelist` MODIFY COLUMN `time` int(11) DEFAULT 0;

-- Verify
SELECT 'All type fixes applied!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_types.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing column types ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_types.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Re-test
print("\n=== Re-test ===")
cmd2 = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "eventAction:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1 | head -c 300
echo ""

echo "eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 300
echo ""

echo "user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 300
echo ""

echo "blacklist:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1 | head -c 300
echo ""
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== Errors ===")
cmd3 = r"""
tail -5 /var/log/httpd/ly_error_log
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
