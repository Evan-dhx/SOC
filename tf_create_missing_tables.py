import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("创建缺失表", r"""
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
CREATE TABLE IF NOT EXISTS `t_asset_host` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `devid` int(10) unsigned NOT NULL,
  `ip` varchar(50) NOT NULL,
  `port` int(10) unsigned NOT NULL,
  `host` varchar(128) NOT NULL,
  `starttime` int(10) unsigned NOT NULL,
  `endtime` int(10) unsigned NOT NULL,
  `duration` int(10) unsigned NOT NULL COMMENT 'minute',
  `is_alive` tinyint(4) NOT NULL,
  `last_hour` int(10) unsigned NOT NULL DEFAULT '0',
  `last_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `flows` int(10) unsigned NOT NULL DEFAULT '0',
  `last_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `last_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `bytes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `ip_port_host` (`ip`,`port`,`host`),
  KEY `st_et` (`starttime`,`endtime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_asset_ip` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `devid` int(10) unsigned NOT NULL,
  `ip` varchar(50) NOT NULL,
  `starttime` int(10) unsigned NOT NULL,
  `endtime` int(10) unsigned NOT NULL,
  `duration` int(10) unsigned NOT NULL COMMENT 'minute',
  `is_alive` tinyint(4) NOT NULL,
  `last_hour` int(10) unsigned NOT NULL DEFAULT '0',
  `last_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `flows` int(10) unsigned NOT NULL DEFAULT '0',
  `last_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `last_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `bytes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `index_ip` (`ip`),
  KEY `st_et` (`starttime`,`endtime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_asset_srv` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `devid` int(10) unsigned NOT NULL,
  `ip` varchar(50) NOT NULL,
  `port` int(10) unsigned NOT NULL,
  `protocol` int(10) unsigned NOT NULL,
  `app_proto` varchar(40) NOT NULL,
  `srv_type` varchar(40) NOT NULL,
  `srv_name` varchar(40) NOT NULL,
  `srv_version` varchar(40) NOT NULL,
  `dev_type` varchar(40) NOT NULL,
  `dev_name` varchar(80) NOT NULL,
  `dev_vendor` varchar(40) NOT NULL,
  `dev_model` varchar(20) NOT NULL,
  `os_type` varchar(40) NOT NULL,
  `os_name` varchar(40) NOT NULL,
  `os_version` varchar(40) NOT NULL,
  `midware_type` varchar(40) NOT NULL,
  `midware_name` varchar(40) NOT NULL,
  `midware_version` varchar(40) NOT NULL,
  `starttime` int(10) unsigned NOT NULL,
  `endtime` int(10) unsigned NOT NULL,
  `duration` int(10) unsigned NOT NULL COMMENT 'minute',
  `is_alive` tinyint(4) NOT NULL,
  `last_hour` int(10) unsigned NOT NULL DEFAULT '0',
  `last_req_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `req_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `last_res_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `res_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `flows` int(10) unsigned NOT NULL DEFAULT '0',
  `last_req_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `req_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `last_res_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `res_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `last_req_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `req_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `last_res_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `res_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `srv_time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `dev_time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `os_time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `midware_time` bigint(20) unsigned NOT NULL DEFAULT '0',
  `threat_time` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `ip_port_proto` (`ip`,`port`,`protocol`),
  KEY `st_et` (`starttime`,`endtime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_asset_url` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `devid` int(10) unsigned NOT NULL,
  `ip` varchar(50) NOT NULL,
  `port` int(10) NOT NULL,
  `url` varchar(256) NOT NULL,
  `retcode` varchar(64) DEFAULT NULL,
  `starttime` int(10) unsigned NOT NULL,
  `endtime` int(10) unsigned NOT NULL,
  `duration` int(10) unsigned NOT NULL COMMENT 'minute',
  `is_alive` tinyint(4) NOT NULL,
  `last_hour` int(10) unsigned NOT NULL DEFAULT '0',
  `last_flows` int(10) unsigned NOT NULL DEFAULT '0',
  `flows` int(10) unsigned NOT NULL DEFAULT '0',
  `last_pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `pkts` int(10) unsigned NOT NULL DEFAULT '0',
  `last_bytes` int(10) unsigned NOT NULL DEFAULT '0',
  `bytes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `ip_port_url` (`ip`,`port`,`url`),
  KEY `st_et` (`starttime`,`endtime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_darkiplist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(50) DEFAULT NULL,
  `mask` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_internal_srv_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(50) NOT NULL,
  `port` int(10) unsigned NOT NULL,
  `desc` varchar(200) NOT NULL,
  `devid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT COUNT(*) AS total_tables FROM information_schema.tables WHERE table_schema='server';
EOF
echo ""
echo "=== 2. 重新统计全部表行数 ==="
mysql -uroot -ppassword123 server -N -e "
SELECT 't_agent', COUNT(*) FROM t_agent UNION ALL
SELECT 't_asset_host', COUNT(*) FROM t_asset_host UNION ALL
SELECT 't_asset_ip', COUNT(*) FROM t_asset_ip UNION ALL
SELECT 't_asset_srv', COUNT(*) FROM t_asset_srv UNION ALL
SELECT 't_asset_url', COUNT(*) FROM t_asset_url UNION ALL
SELECT 't_blacklist', COUNT(*) FROM t_blacklist UNION ALL
SELECT 't_config', COUNT(*) FROM t_config UNION ALL
SELECT 't_darkiplist', COUNT(*) FROM t_darkiplist UNION ALL
SELECT 't_device', COUNT(*) FROM t_device UNION ALL
SELECT 't_event_action', COUNT(*) FROM t_event_action UNION ALL
SELECT 't_event_data', COUNT(*) FROM t_event_data UNION ALL
SELECT 't_event_data_aggre', COUNT(*) FROM t_event_data_aggre UNION ALL
SELECT 't_event_ignore', COUNT(*) FROM t_event_ignore UNION ALL
SELECT 't_event_level', COUNT(*) FROM t_event_level UNION ALL
SELECT 't_event_list', COUNT(*) FROM t_event_list UNION ALL
SELECT 't_event_status', COUNT(*) FROM t_event_status UNION ALL
SELECT 't_event_type', COUNT(*) FROM t_event_type UNION ALL
SELECT 't_internal_ip_list', COUNT(*) FROM t_internal_ip_list UNION ALL
SELECT 't_internal_srv_list', COUNT(*) FROM t_internal_srv_list UNION ALL
SELECT 't_mo', COUNT(*) FROM t_mo UNION ALL
SELECT 't_mogroup', COUNT(*) FROM t_mogroup UNION ALL
SELECT 't_url_attack_type', COUNT(*) FROM t_url_attack_type UNION ALL
SELECT 't_user', COUNT(*) FROM t_user UNION ALL
SELECT 't_whitelist', COUNT(*) FROM t_whitelist;" 2>&1
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
