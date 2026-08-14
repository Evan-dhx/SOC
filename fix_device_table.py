import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_device: rename temp to template, ensure all columns exist
ALTER TABLE `t_device` CHANGE `temp` `template` varchar(256) DEFAULT '';

-- Verify t_device structure
DESCRIBE `t_device`;

-- Fix t_event_ignore: the SELECT query uses specific columns
-- Let's check what config_event.cpp queries for event_ignore
-- From the error: Unknown column 'time' - we changed it to bigint but the query might expect datetime
-- The code uses: SELECT `id`, `time`, `lip`, `tip`, `tport`, `protocol`, `domain`, `desc`, `weekday`, `stime`, `etime`, `coverrange`,`count` FROM `t_event_ignore`
-- And uses FROM_UNIXTIME(?) for time - so time should be stored as unix timestamp (bigint)
-- But the SELECT returns `time` directly - let's check if the issue is the column type

-- Actually the issue might be that the SELECT expects `time` as a specific type
-- Let's just make sure all columns exist with correct types
DESCRIBE `t_event_ignore`;

-- Fix t_blacklist and t_whitelist: check what columns config_bwlist.so needs
DESCRIBE `t_blacklist`;
DESCRIBE `t_whitelist`;

-- Fix t_user: check what config_user.so needs
DESCRIBE `t_user`;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_device.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing tables ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_device.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Re-test device API
print("\n=== Re-test device API ===")
cmd2 = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "deviceApi:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1 | head -c 300
echo ""

echo "eventAction:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1 | head -c 300
echo ""

echo "eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 300
echo ""

echo "blacklist:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1 | head -c 300
echo ""

echo "user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 300
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
