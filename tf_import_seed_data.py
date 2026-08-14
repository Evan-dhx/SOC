import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("导入官方种子数据", r"""
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
-- 1. 重建与代码不匹配的表（官方结构）
DROP TABLE IF EXISTS `t_event_config_icmp_tunnel`;
CREATE TABLE `t_event_config_icmp_tunnel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sip` varchar(64) DEFAULT '',
  `dip` varchar(64) DEFAULT '',
  `IF1` int(11) NOT NULL DEFAULT '5',
  `IF2` int(11) NOT NULL DEFAULT '2',
  `IF3` int(11) NOT NULL DEFAULT '5',
  `desc` varchar(200) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_event_config_frn_trip`;
CREATE TABLE `t_event_config_frn_trip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sip` varchar(64) DEFAULT '',
  `dip` varchar(64) DEFAULT '',
  `min` int(11) NOT NULL DEFAULT '0',
  `desc` varchar(200) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `t_event_config_dnstunnel`;
CREATE TABLE `t_event_config_dnstunnel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(64) DEFAULT '',
  `namelen` int(11) NOT NULL DEFAULT '52',
  `fqcount` int(11) NOT NULL DEFAULT '150',
  `detvalue` int(11) NOT NULL DEFAULT '5000',
  `desc` varchar(200) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 创建缺失的 t_url_attack_type
CREATE TABLE IF NOT EXISTS `t_url_attack_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. t_mogroup（官方 5 组）
DELETE FROM `t_mogroup`;
INSERT INTO `t_mogroup`(`id`,`name`) VALUES (1,'Unclassified'),(2,'Incoming'),(3,'Outgoing'),(4,'Observed'),(5,'Abnormal');

-- 4. t_mo（官方 32 条，devid 3->1）
DELETE FROM `t_mo`;
INSERT INTO `t_mo`(`id`,`moip`,`moport`,`protocol`,`pip`,`pport`,`modesc`,`tag`,`mogroupid`,`filter`,`devid`,`direction`) VALUES
(1,'','0','','','','Port 0 traffic','',5,'port 0 and not proto ICMP',1,'ALL'),
(2,'','22','','','','SSH traffic','',4,'port 22',1,'ALL'),
(3,'','3389','','','','RDP traffic','',4,'port 3389',1,'ALL'),
(4,'','5800','','','','VNC traffic','',4,'port 5800',1,'ALL'),
(5,'','5900','','','','VNC traffic','',4,'port 5900',1,'ALL'),
(6,'','6000','','','','X11 traffic','',4,'port 6000',1,'ALL'),
(7,'','3306','','','','MySQL/MariaDB','',4,'port 3306',1,'ALL'),
(8,'','1521','','','','Oracle traffic','',4,'port 1521',1,'ALL'),
(9,'','1433','','','','SQLServer traffic','',4,'port 1433',1,'ALL'),
(10,'','5000','','','','DB2 traffic','',4,'port 5000',1,'ALL'),
(11,'','5432','','','','psotgreSQL traffic','',4,'port 5432',1,'ALL'),
(12,'','9300','','','','Elasticsearch traffic','',4,'port 9300',1,'ALL'),
(13,'','27017','','','','MongoDB traffic','',4,'port 27017',1,'ALL'),
(14,'','6379','','','','Redis traffic','',4,'port 6379',1,'ALL'),
(15,'','11211','','','','memcached traffic','',4,'port 11211',1,'ALL'),
(16,'','80','','','','HTTP traffic','',4,'port 80',1,'ALL'),
(17,'','8080','','','','HTTP traffic','',4,'port 8080',1,'ALL'),
(18,'','443','','','','HTTPs traffic','',4,'port 443',1,'ALL'),
(19,'','25','','','','SMTP traffic','',4,'port 25',1,'ALL'),
(20,'','110','','','','POP3 traffic','',4,'port 110',1,'ALL'),
(21,'','465','','','','SMTPs/IMAP traffic','',4,'port 465',1,'ALL'),
(22,'','995','','','','POP3s traffic','',4,'port 995',1,'ALL'),
(23,'','993','','','','IMAP traffic','',4,'port 993',1,'ALL'),
(24,'','161','','','','SNMP traffic','',4,'port 161',1,'ALL'),
(25,'','162','','','','SNMP(Trap) traffic','',4,'port 162',1,'ALL'),
(26,'','514','','','','Syslog traffic','',4,'port 514',1,'ALL'),
(27,'','123','','','','NTP traffic','',4,'port 123',1,'ALL'),
(28,'','22','','','','SSH response','',3,'src port 22',1,'OUT'),
(29,'','3389','','','','RDP response','',3,'src port 3389',1,'OUT'),
(30,'','22','','','','SSH request','',2,'dst port 22',1,'IN'),
(31,'','3389','','','','RDP request','',2,'dst port 3389',1,'IN'),
(32,'','0','','','','ICMP traffic','',1,'proto ICMP',1,'ALL');

-- 5. t_event_config_*（官方 12 条）
DELETE FROM `t_event_config_black`;
INSERT INTO `t_event_config_black`(`id`,`data_type`,`min`,`max`) VALUES (1,'Bps',1,NULL);
DELETE FROM `t_event_config_sus`;
INSERT INTO `t_event_config_sus`(`id`,`data_type`,`min`,`max`) VALUES (1,'Bps',1,NULL);
DELETE FROM `t_event_config_dga`;
INSERT INTO `t_event_config_dga`(`id`,`sip`,`dip`,`qcount`,`min`) VALUES (1,NULL,NULL,50,99);
DELETE FROM `t_event_config_dns`;
INSERT INTO `t_event_config_dns`(`id`,`ip`,`qname`,`qcount`,`desc`) VALUES (1,NULL,NULL,0,'Ti domain query');
DELETE FROM `t_event_config_dnstunnel`;
INSERT INTO `t_event_config_dnstunnel`(`id`,`ip`,`namelen`,`fqcount`,`detvalue`,`desc`) VALUES (1,NULL,52,150,5000,'Dns tunnel traffic');
DELETE FROM `t_event_config_icmp_tunnel`;
INSERT INTO `t_event_config_icmp_tunnel`(`id`,`sip`,`dip`,`IF1`,`IF2`,`IF3`,`desc`) VALUES (1,'','',5,2,5,'');
DELETE FROM `t_event_config_ip_scan`;
INSERT INTO `t_event_config_ip_scan`(`id`,`min_peerports`,`max_peerports`,`sip`,`dip`,`protocol`) VALUES (1,1000,NULL,NULL,NULL,NULL);
DELETE FROM `t_event_config_port_scan`;
INSERT INTO `t_event_config_port_scan`(`id`,`min_peerips`,`max_peerips`,`ip`,`port`,`protocol`) VALUES (1,1000,NULL,NULL,NULL,NULL),(2,300,NULL,NULL,22,NULL),(3,300,NULL,NULL,3389,NULL);
DELETE FROM `t_event_config_srv`;
INSERT INTO `t_event_config_srv`(`id`,`min_portsessions`,`max_portsessions`,`ip`,`port`,`protocol`) VALUES (1,3000,NULL,'',NULL,NULL),(2,300,NULL,'',22,NULL),(3,300,NULL,'',3389,NULL);

-- 6. t_event_type（15 条）
DELETE FROM `t_event_type`;
INSERT INTO `t_event_type`(`id`,`desc`) VALUES (1,'mo'),(2,'port_scan'),(3,'srv'),(4,'dns'),(5,'black'),(6,'ti'),(7,'dns_tun'),(8,'ip_scan'),(9,'url_content'),(10,'frn_trip'),(11,'icmp_tun'),(12,'dga'),(13,'cap'),(14,'dnstun_ai'),(15,'mining');

-- 7. t_event_status（15 条）
DELETE FROM `t_event_status`;
INSERT INTO `t_event_status`(`id`,`moid`,`status`) VALUES (1,NULL,'ON'),(2,NULL,'ON'),(3,NULL,'ON'),(4,NULL,'ON'),(5,NULL,'ON'),(6,NULL,'ON'),(7,NULL,'ON'),(8,NULL,'ON'),(9,NULL,'ON'),(10,NULL,'ON'),(11,NULL,'ON'),(12,NULL,'ON'),(13,NULL,'ON'),(14,NULL,'ON'),(15,NULL,'ON');

-- 8. t_event_level（7 条）
DELETE FROM `t_event_level`;
INSERT INTO `t_event_level`(`id`,`desc`,`profile`) VALUES (1,'extra_high',''),(2,'high',''),(3,'middle',''),(4,'low',''),(5,'extra_low',''),(6,'auto_tight','20:50:100:200'),(7,'auto_loose','100:500:1000:5000');

-- 9. t_event_list（15 条规则）
DELETE FROM `t_event_list`;
INSERT INTO `t_event_list`(`id`,`type_id`,`config_id`,`level_id`,`action_id`,`status_id`,`desc`,`devid`,`weekday`,`stime`,`etime`,`coverrange`) VALUES
(1,7,1,7,'1',1,'Dns tunnel traffic',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(2,5,1,1,'1',2,'Blacklist traffic Bps (>1)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(3,2,1,7,'1',3,'Scan peers (>1k)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(4,2,2,6,'1',4,'SSH peers (>300)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(5,2,3,6,'1',5,'RDP peers (>300)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(6,3,1,7,'1',6,'Service sessions (>3k)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(7,3,2,6,'1',7,'SSH sessions (>300)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(8,3,3,6,'1',8,'RDP sessions (>300)',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(9,4,1,7,'1',9,'Ti domain query',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(10,13,1,7,'1',10,'Threat',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(11,6,1,7,'1',11,'Ti IP',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(12,15,1,7,'1',12,'Mining',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(13,12,1,1,'1',13,'DGA',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(14,11,1,1,'1',14,'ICMP Tunnel',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within'),
(15,8,1,1,'1',15,'IP scan init config',NULL,'0,1,2,3,4,5,6','00:00:00','23:59:59','within');

-- 10. t_event_action（官方 1 条）
DELETE FROM `t_event_action`;
INSERT INTO `t_event_action`(`id`,`act`,`mail`,`phone`,`uid`,`desc`) VALUES (1,1,'mailname@mailservername.com','','','Admin mail');

-- 11. t_internal_ip_list（保留现有 + 官方 0.0.0.0/0）
INSERT INTO `t_internal_ip_list`(`ip`,`devid`,`desc`) VALUES ('0.0.0.0/0',1,'') ON DUPLICATE KEY UPDATE ip=ip;

-- 12. t_url_attack_type（5 条）
DELETE FROM `t_url_attack_type`;
INSERT INTO `t_url_attack_type`(`id`,`desc`) VALUES (1,'sql_inject'),(2,'xss'),(3,'reso_explore'),(4,'visit_admin'),(5,'pull_db');

-- 验证
SELECT 't_mo' t, COUNT(*) c FROM t_mo UNION ALL SELECT 't_mogroup', COUNT(*) FROM t_mogroup UNION ALL SELECT 't_event_type', COUNT(*) FROM t_event_type UNION ALL SELECT 't_event_list', COUNT(*) FROM t_event_list UNION ALL SELECT 't_event_status', COUNT(*) FROM t_event_status UNION ALL SELECT 't_event_level', COUNT(*) FROM t_event_level UNION ALL SELECT 't_event_config_black', COUNT(*) FROM t_event_config_black UNION ALL SELECT 't_event_config_sus', COUNT(*) FROM t_event_config_sus UNION ALL SELECT 't_event_config_dga', COUNT(*) FROM t_event_config_dga UNION ALL SELECT 't_event_config_dns', COUNT(*) FROM t_event_config_dns UNION ALL SELECT 't_event_config_dnstunnel', COUNT(*) FROM t_event_config_dnstunnel UNION ALL SELECT 't_event_config_icmp_tunnel', COUNT(*) FROM t_event_config_icmp_tunnel UNION ALL SELECT 't_event_config_ip_scan', COUNT(*) FROM t_event_config_ip_scan UNION ALL SELECT 't_event_config_port_scan', COUNT(*) FROM t_event_config_port_scan UNION ALL SELECT 't_event_config_srv', COUNT(*) FROM t_event_config_srv UNION ALL SELECT 't_url_attack_type', COUNT(*) FROM t_url_attack_type;
EOF
echo "导入完成"
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
