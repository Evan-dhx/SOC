import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_event_ignore: change time column type (do it separately to avoid earlier error)
UPDATE `t_event_ignore` SET `time` = 0 WHERE `time` = '' OR `time` IS NULL;
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` int(11) DEFAULT 0;

-- Fix t_user: add 'desc' column (config_user.so queries it)
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '' AFTER `resource`;

-- Also add 'createtime' as datetime if config_user expects datetime
-- The config_user.cpp SELECT: `id`, `name`, `lasttime`, `lastip`, `level`, `createtime`, `comment`, `disabled`, `creator`, `lockedtime`, `resource`
-- Our table has lasttime as int - config_user might read it as datetime
-- Let's check by looking at the output code
-- For now, just make sure all columns exist

SELECT 'Fixes applied!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_last.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Applying fixes ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_last.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Re-test
print("\n=== Re-test ===")
cmd2 = r"""
> /var/log/httpd/ly_error_log
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 300
echo ""

echo "user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 300
echo ""

echo "=== Errors ==="
cat /var/log/httpd/ly_error_log
echo "(end)"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
