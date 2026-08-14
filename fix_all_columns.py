import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_event_action: add 'desc' column
ALTER TABLE `t_event_action` ADD COLUMN IF NOT EXISTS `desc` varchar(128) DEFAULT '' AFTER `uid`;

-- Fix t_event_ignore: add 'time' column as bigint (unix timestamp)
-- The code uses FROM_UNIXTIME(?) so time should be stored as unix timestamp
-- But the SELECT uses `time` column - let's check what type it needs
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` bigint(20) DEFAULT 0;

-- Fix t_event_ignore: the code also selects 'count' column - make sure it exists
-- (already created with count)

-- Check what columns config_bwlist.so needs
-- The bwlist table needs: id, ip, port, desc, time
ALTER TABLE `t_blacklist` ADD COLUMN IF NOT EXISTS `time` bigint(20) DEFAULT 0 AFTER `port`;
ALTER TABLE `t_whitelist` ADD COLUMN IF NOT EXISTS `time` bigint(20) DEFAULT 0 AFTER `port`;

-- Fix t_user: the user config needs specific columns
-- Check what config_user.so queries
-- From config_user.proto: id, uid, username, pass, level, comment, disabled, lockedtime, resource
-- Our t_user has: id, name, pass, level, resource, disabled, lockedtime, lasttime, lastip, lastsession
-- Need to add: uid, username, comment
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `uid` int(11) DEFAULT 0 AFTER `id`;
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `username` varchar(64) DEFAULT '' AFTER `name`;
ALTER TABLE `t_user` ADD COLUMN IF NOT EXISTS `comment` varchar(256) DEFAULT '' AFTER `level`;

-- Update admin user with username
UPDATE `t_user` SET `username`='admin', `uid`=1 WHERE `name`='admin';

-- Fix t_event_config tables: they might need 'desc' column too
-- All event_config tables need: config_id, devid, desc
-- Let's add desc to all that don't have it
ALTER TABLE `t_event_config_threshold` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_port_scan` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_ip_scan` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_srv` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_sus` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_black` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_dns` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_dnstunnel` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_url_content` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_frn_trip` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_icmp_tunnel` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_dnstun_ai` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';
ALTER TABLE `t_event_config_dga` ADD COLUMN IF NOT EXISTS `desc` varchar(256) DEFAULT '';

SELECT 'All columns fixed!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_cols.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing columns ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_cols.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
if err:
    print(f"STDERR: {err}")

# Now re-test all endpoints
print("\n=== Re-test all endpoints ===")
cmd2 = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "1. deviceApi:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1 | head -c 200
echo ""

echo "2. eventConfig:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_config" 2>&1 | head -c 200
echo ""

echo "3. eventAction:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1 | head -c 200
echo ""

echo "4. eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 200
echo ""

echo "5. blacklist:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1 | head -c 200
echo ""

echo "6. user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 200
echo ""

echo "7. eventType:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_type" 2>&1 | head -c 200
echo ""

echo "8. eventLevel:"
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
