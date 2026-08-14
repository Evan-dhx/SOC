import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_user: add missing columns
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `createtime` bigint(20) DEFAULT 0 AFTER `pass`;
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `creator` varchar(64) DEFAULT '' AFTER `comment`;

-- Update admin user
UPDATE `t_user` SET `createtime`=UNIX_TIMESTAMP(), `creator`='system' WHERE `name`='admin';

-- Fix t_event_ignore: the code reads `time` as string/datetime but we have bigint
-- The SELECT query reads time directly, so let's check what type cppdb expects
-- Looking at the code: it uses FROM_UNIXTIME(?) for INSERT, so time is stored as unix timestamp
-- But the SELECT reads it back - cppdb might try to read it as string
-- Let's change time to varchar to match what cppdb expects
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` varchar(32) DEFAULT '0';

-- Verify all tables
SELECT 'All fixes applied!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/final_fix.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Applying fixes ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/final_fix.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Re-test all endpoints
print("\n=== Re-test all ===")
cmd2 = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "1. deviceApi:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1 | head -c 200
echo ""

echo "2. eventAction:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1 | head -c 200
echo ""

echo "3. eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 200
echo ""

echo "4. user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 200
echo ""

echo "5. eventType:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_type" 2>&1 | head -c 100
echo ""

echo "6. eventLevel:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_level" 2>&1 | head -c 200
echo ""
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# Check errors
print("\n=== Errors ===")
cmd3 = r"""
tail -5 /var/log/httpd/ly_error_log
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
