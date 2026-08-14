import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_event_ignore: time should be datetime (code reads as struct tm)
ALTER TABLE `t_event_ignore` MODIFY COLUMN `time` datetime DEFAULT NULL;

-- Insert a sample event_ignore record for testing
INSERT INTO `t_event_ignore` (`time`, `lip`, `tip`, `tport`, `protocol`, `domain`, `desc`, `weekday`, `stime`, `etime`, `coverrange`, `count`) VALUES
(NOW(), '10.0.0.0/8', '', 0, '', '', '內部網絡忽略', '*', '00:00', '23:59', 'all', 0);

SELECT 'event_ignore fixed!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_ignore.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing event_ignore ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_ignore.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Rebuild config_event.so
print("\n=== Rebuild config_event.so ===")
cmd2 = r"""
cd /root/SOC/ly_server_src/lib
make config_event.so 2>&1 | tail -5
cp config_event.so /Server/lib/
echo "Deployed"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# Test
print("\n=== Test ===")
cmd3 = r"""
> /var/log/httpd/ly_error_log
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "eventIgnore:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 300
echo ""

echo ""
echo "Errors:"
cat /var/log/httpd/ly_error_log
echo "(end)"
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
