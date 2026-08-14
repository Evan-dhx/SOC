import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Fix t_event_action: add missing columns
ALTER TABLE `t_event_action`
  ADD COLUMN `act` varchar(64) DEFAULT '' AFTER `id`,
  ADD COLUMN `mail` varchar(256) DEFAULT '',
  ADD COLUMN `phone` varchar(64) DEFAULT '',
  ADD COLUMN `uid` int(11) DEFAULT 0;

-- Fix t_event_list: add missing columns
ALTER TABLE `t_event_list`
  ADD COLUMN `type_id` int(11) DEFAULT 0 AFTER `id`,
  ADD COLUMN `level_id` int(11) DEFAULT 0,
  ADD COLUMN `action_id` int(11) DEFAULT 0,
  ADD COLUMN `status_id` int(11) DEFAULT 0,
  ADD COLUMN `desc` varchar(256) DEFAULT '';

-- Fix t_event_status: add moid column
ALTER TABLE `t_event_status`
  ADD COLUMN `moid` int(11) DEFAULT 0 AFTER `id`,
  ADD COLUMN `status` varchar(32) DEFAULT '';

-- Fix t_event_ignore: add desc column (already has it, check)
-- Add desc to t_event_ignore if missing
-- (already created with desc)

-- Insert default event action
INSERT INTO `t_event_action` (`act`, `mail`, `phone`, `uid`, `desc`) VALUES
('alert', '', '', 0, '告警'),
('log', '', '', 0, '記錄'),
('block', '', '', 0, '阻斷')
ON DUPLICATE KEY UPDATE `act`=`act`;

-- Insert default event status
INSERT INTO `t_event_status` (`moid`, `status`) VALUES
(0, 'enabled'),
(0, 'disabled')
ON DUPLICATE KEY UPDATE `status`=`status`;

SELECT 'Tables fixed!' AS status;
"""

sftp = client.open_sftp()
with sftp.file('/tmp/fix_tables.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Fixing tables ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/fix_tables.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
if err:
    print(f"STDERR: {err}")

# Test config endpoint again
print("\n=== Test config ===")
cmd2 = r"""
curl -s http://localhost/d/config 2>&1 | head -5
echo "---"
tail -3 /var/log/httpd/ly_error_log
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
