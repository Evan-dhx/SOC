import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- First clear data that has empty strings in int columns
UPDATE `t_event_action` SET `act` = 0 WHERE `act` = '' OR `act` IS NULL;
UPDATE `t_event_action` SET `uid` = 0 WHERE `uid` = '' OR `uid` IS NULL;

-- Now change column types
ALTER TABLE `t_event_action` MODIFY COLUMN `act` int(11) DEFAULT 0;
ALTER TABLE `t_event_action` MODIFY COLUMN `uid` int(11) DEFAULT 0;

-- Fix t_event_ignore
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` int(11) DEFAULT 0;
ALTER TABLE `t_event_ignore` MODIFY COLUMN `tport` int(11) DEFAULT 0;
ALTER TABLE `t_event_ignore` MODIFY COLUMN `count` int(11) DEFAULT 0;

-- Fix blacklist/whitelist
ALTER TABLE `t_blacklist` MODIFY COLUMN `time` int(11) DEFAULT 0;
ALTER TABLE `t_whitelist` MODIFY COLUMN `time` int(11) DEFAULT 0;

-- Re-insert default event actions with correct types
DELETE FROM `t_event_action`;
INSERT INTO `t_event_action` (`act`, `mail`, `phone`, `uid`, `desc`) VALUES
(1, '', '', 0, '告警'),
(2, '', '', 0, '記錄'),
(3, '', '', 0, '阻斷');

SELECT 'All type fixes done!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_types2.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing types ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_types2.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Rebuild config .so files to ensure they match current code
print("\n=== Rebuild config libs ===")
cmd2 = r"""
cd /root/SOC/ly_server_src/lib
make clean 2>/dev/null
make 2>&1 | tail -10
echo "Build: ${PIPESTATUS[0]}"
cp *.so /Server/lib/
echo "Deployed"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

# Clear error log and re-test
print("\n=== Re-test ===")
cmd3 = r"""
> /var/log/httpd/ly_error_log
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "eventAction:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1
echo ""

echo "eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1
echo ""

echo "user:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 300
echo ""

echo "blacklist:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1
echo ""

echo "deviceApi:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1 | head -c 200
echo ""
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== Errors ===")
cmd4 = r"""
cat /var/log/httpd/ly_error_log
echo "(end)"
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
