import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Drop and recreate all event_config tables with correct schema
sql = """
-- Drop old tables
DROP TABLE IF EXISTS `t_event_config_threshold`;
DROP TABLE IF EXISTS `t_event_config_port_scan`;
DROP TABLE IF EXISTS `t_event_config_ip_scan`;
DROP TABLE IF EXISTS `t_event_config_srv`;
DROP TABLE IF EXISTS `t_event_config_sus`;
DROP TABLE IF EXISTS `t_event_config_black`;
DROP TABLE IF EXISTS `t_event_config_dns`;
DROP TABLE IF EXISTS `t_event_config_dnstunnel`;
DROP TABLE IF EXISTS `t_event_config_url_content`;
DROP TABLE IF EXISTS `t_event_config_frn_trip`;
DROP TABLE IF EXISTS `t_event_config_icmp_tunnel`;
DROP TABLE IF EXISTS `t_event_config_dnstun_ai`;
DROP TABLE IF EXISTS `t_event_config_dga`;

-- Recreate with correct schema based on code analysis

-- t_event_config_threshold: SELECT id, moid, thres_mode, data_type, min, max, grep_rule
CREATE TABLE `t_event_config_threshold` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `moid` int(11) DEFAULT 0,
  `thres_mode` varchar(32) DEFAULT '',
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  `grep_rule` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_port_scan: SELECT id, min_peerips, max_peerips, ip, port, protocol
CREATE TABLE `t_event_config_port_scan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `min_peerips` int(11) DEFAULT 0,
  `max_peerips` int(11) DEFAULT 0,
  `ip` varchar(64) DEFAULT '',
  `port` varchar(32) DEFAULT '',
  `protocol` varchar(16) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_ip_scan: SELECT id, min_peerports, max_peerports, sip, dip, protocol
CREATE TABLE `t_event_config_ip_scan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `min_peerports` int(11) DEFAULT 0,
  `max_peerports` int(11) DEFAULT 0,
  `sip` varchar(64) DEFAULT '',
  `dip` varchar(64) DEFAULT '',
  `protocol` varchar(16) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_srv: SELECT id, min_portsessions, max_portsessions, ip, port, protocol
CREATE TABLE `t_event_config_srv` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `min_portsessions` int(11) DEFAULT 0,
  `max_portsessions` int(11) DEFAULT 0,
  `ip` varchar(64) DEFAULT '',
  `port` varchar(32) DEFAULT '',
  `protocol` varchar(16) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_sus: SELECT id, data_type, min, max
CREATE TABLE `t_event_config_sus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_black: SELECT id, data_type, min, max
CREATE TABLE `t_event_config_black` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_dns: SELECT id, ip, qname, qcount, desc
CREATE TABLE `t_event_config_dns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT '',
  `qname` varchar(256) DEFAULT '',
  `qcount` int(11) DEFAULT 0,
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_dnstunnel: need to check
CREATE TABLE `t_event_config_dnstunnel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_url_content: SELECT id, type, min, pat
CREATE TABLE `t_event_config_url_content` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `pat` varchar(512) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_frn_trip
CREATE TABLE `t_event_config_frn_trip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_icmp_tunnel
CREATE TABLE `t_event_config_icmp_tunnel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` varchar(32) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  `max` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_dnstun_ai: SELECT id, sip, dip, min
CREATE TABLE `t_event_config_dnstun_ai` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sip` varchar(64) DEFAULT '',
  `dip` varchar(64) DEFAULT '',
  `min` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- t_event_config_dga: SELECT id, sip, dip, qcount, min
CREATE TABLE `t_event_config_dga` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sip` varchar(64) DEFAULT '',
  `dip` varchar(64) DEFAULT '',
  `qcount` int(11) DEFAULT 0,
  `min` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'All event_config tables recreated!' AS status;
SHOW TABLES LIKE 't_event_config%';
"""

sftp = client.open_sftp()
with sftp.file('/tmp/recreate_event_config.sql', 'w') as f:
    f.write(sql)
sftp.close()

print("=== Recreating event_config tables ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/recreate_event_config.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test event_config endpoint
print("\n=== Test event_config ===")
cmd2 = r"""
> /var/log/httpd/ly_error_log
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "eventConfig response:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_config" 2>&1 | head -c 300
echo ""

echo ""
echo "Errors:"
cat /var/log/httpd/ly_error_log
echo "(end)"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
