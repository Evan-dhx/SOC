import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sql = """
-- Device and Agent tables
CREATE TABLE IF NOT EXISTS `t_agent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT '',
  `ip` varchar(64) DEFAULT '',
  `creator` varchar(64) DEFAULT '',
  `status` varchar(32) DEFAULT '',
  `comment` varchar(256) DEFAULT '',
  `disabled` char(1) DEFAULT 'N',
  `serial` varchar(128) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT '',
  `type` varchar(32) DEFAULT '',
  `model` varchar(64) DEFAULT '',
  `agentid` int(11) DEFAULT 0,
  `creator` varchar(64) DEFAULT '',
  `comment` varchar(256) DEFAULT '',
  `ip` varchar(64) DEFAULT '',
  `port` int(11) DEFAULT 0,
  `disabled` char(1) DEFAULT 'N',
  `flowtype` varchar(32) DEFAULT '',
  `interface` varchar(64) DEFAULT '',
  `pcap_level` int(11) DEFAULT 0,
  `temp` varchar(256) DEFAULT '',
  `filter` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Event config tables (one per detection type)
CREATE TABLE IF NOT EXISTS `t_event_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_id` int(11) DEFAULT 0,
  `devid` int(11) DEFAULT 0,
  `weekday` varchar(32) DEFAULT '',
  `stime` varchar(16) DEFAULT '',
  `etime` varchar(16) DEFAULT '',
  `coverrange` varchar(32) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(128) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_level` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(64) DEFAULT '',
  `profile` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_action` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(128) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_ignore` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lip` varchar(64) DEFAULT '',
  `tip` varchar(64) DEFAULT '',
  `tport` int(11) DEFAULT 0,
  `protocol` varchar(16) DEFAULT '',
  `domain` varchar(256) DEFAULT '',
  `weekday` varchar(32) DEFAULT '',
  `stime` varchar(16) DEFAULT '',
  `etime` varchar(16) DEFAULT '',
  `coverrange` varchar(32) DEFAULT '',
  `count` int(11) DEFAULT 0,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Event config per detection type (all share similar structure)
CREATE TABLE IF NOT EXISTS `t_event_config_threshold` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_port_scan` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_ip_scan` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_srv` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `srv_name` varchar(64) DEFAULT '',
  `srv_type` varchar(32) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_sus` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_black` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_dns` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_dnstunnel` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_url_content` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `url` varchar(512) DEFAULT '',
  `content` varchar(512) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_frn_trip` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_icmp_tunnel` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_dnstun_ai` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_config_dga` (
  `config_id` int(11) NOT NULL AUTO_INCREMENT,
  `devid` int(11) DEFAULT 0,
  `thres_type` varchar(32) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Blacklist / Whitelist
CREATE TABLE IF NOT EXISTS `t_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT '',
  `port` varchar(32) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_whitelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT '',
  `port` varchar(32) DEFAULT '',
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MO (Monitored Object) tables
CREATE TABLE IF NOT EXISTS `t_mo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `moip` varchar(64) DEFAULT '',
  `moport` varchar(32) DEFAULT '',
  `protocol` varchar(16) DEFAULT '',
  `pip` varchar(64) DEFAULT '',
  `pport` varchar(32) DEFAULT '',
  `modesc` varchar(256) DEFAULT '',
  `tag` varchar(64) DEFAULT '',
  `mogroupid` int(11) DEFAULT 0,
  `filter` varchar(512) DEFAULT '',
  `devid` int(11) DEFAULT 0,
  `direction` varchar(16) DEFAULT 'ALL',
  `addtime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_mogroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Internal IP list
CREATE TABLE IF NOT EXISTS `t_internal_ip_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT '',
  `devid` int(11) DEFAULT 0,
  `desc` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Event data tables
CREATE TABLE IF NOT EXISTS `t_event_data_aggre` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) DEFAULT 0,
  `devid` int(11) DEFAULT 0,
  `obj` varchar(256) DEFAULT '',
  `type` varchar(64) DEFAULT '',
  `model` int(11) DEFAULT 0,
  `level` varchar(32) DEFAULT '',
  `alarm_peak` bigint(20) DEFAULT 0,
  `sub_events` int(11) DEFAULT 0,
  `alarm_avg` bigint(20) DEFAULT 0,
  `value_type` varchar(32) DEFAULT '',
  `desc` varchar(512) DEFAULT '',
  `duration` bigint(20) DEFAULT 0,
  `starttime` bigint(20) DEFAULT 0,
  `endtime` bigint(20) DEFAULT 0,
  `is_alive` tinyint(1) DEFAULT 1,
  `proc_status` varchar(32) DEFAULT '',
  `proc_comment` varchar(256) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_event_id` (`event_id`),
  KEY `idx_devid` (`devid`),
  KEY `idx_is_alive` (`is_alive`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_event_data` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `time` bigint(20) DEFAULT 0,
  `event_id` int(11) DEFAULT 0,
  `type` varchar(64) DEFAULT '',
  `model` int(11) DEFAULT 0,
  `devid` int(11) DEFAULT 0,
  `level` varchar(32) DEFAULT '',
  `obj` varchar(256) DEFAULT '',
  `thres_value` varchar(64) DEFAULT '',
  `alarm_value` varchar(64) DEFAULT '',
  `value_type` varchar(32) DEFAULT '',
  `desc` varchar(512) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_event_id` (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default event types
INSERT INTO `t_event_type` (`id`, `desc`) VALUES
(1, '端口扫描'), (2, 'IP扫描'), (3, '异常服务'), (4, '可疑行为'),
(5, '黑名单命中'), (6, 'DNS异常'), (7, 'DNS隧道'), (8, 'URL内容'),
(9, '外连三元组'), (10, 'ICMP隧道'), (11, 'DNS隧道AI'), (12, 'DGA'),
(13, '阈值告警')
ON DUPLICATE KEY UPDATE `desc`=`desc`;

-- Insert default event levels
INSERT INTO `t_event_level` (`id`, `desc`, `profile`) VALUES
(1, '低', 'low'), (2, '中', 'medium'), (3, '高', 'high'), (4, '严重', 'critical')
ON DUPLICATE KEY UPDATE `desc`=`desc`;

-- Insert default event status
INSERT INTO `t_event_status` (`id`, `desc`) VALUES
(1, '启用'), (2, '禁用')
ON DUPLICATE KEY UPDATE `desc`=`desc`;

-- Insert default event actions
INSERT INTO `t_event_action` (`id`, `desc`) VALUES
(1, '告警'), (2, '记录'), (3, '阻断')
ON DUPLICATE KEY UPDATE `desc`=`desc`;

-- Insert default admin device and agent
INSERT INTO `t_agent` (`id`, `name`, `ip`, `status`) VALUES
(1, '默认分析节点', '127.0.0.1', 'active')
ON DUPLICATE KEY UPDATE `name`=`name`;

INSERT INTO `t_device` (`id`, `name`, `type`, `agentid`, `ip`, `status`) VALUES
(1, '默认设备', 'netflow', 1, '127.0.0.1', 'active')
ON DUPLICATE KEY UPDATE `name`=`name`;

SELECT 'All tables created successfully!' AS status;
SHOW TABLES;
"""

# Write SQL file
sftp = client.open_sftp()
with sftp.file('/tmp/create_all_tables.sql', 'w') as f:
    f.write(sql)
sftp.close()

# Execute
print("=== Creating all tables ===")
cmd = r"""
mysql -u root -p'password123' server < /tmp/create_all_tables.sql 2>&1
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
if err:
    print(f"STDERR: {err}")

# Test the config endpoint
print("\n=== Test config endpoint ===")
cmd2 = r"""
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/config
curl -s http://localhost/d/config 2>&1 | head -3
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check error log
print("\n=== Latest errors ===")
cmd3 = r"""
tail -5 /var/log/httpd/ly_error_log
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
