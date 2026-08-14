import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重建 t_user 为官方结构", r"""
echo "=== 1. 重建 t_user ==="
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL DEFAULT '',
  `pass` varchar(100) DEFAULT '',
  `lasttime` int(11) DEFAULT NULL,
  `lastip` int(10) unsigned DEFAULT NULL,
  `level` varchar(10) DEFAULT 'viewer',
  `createtime` int(11) DEFAULT NULL,
  `comment` varchar(200) DEFAULT NULL,
  `disabled` char(1) DEFAULT 'N',
  `creator` varchar(50) DEFAULT '',
  `lockedtime` bigint(20) NOT NULL DEFAULT '0',
  `lastsession` char(32) NOT NULL DEFAULT '',
  `resource` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `t_user`(`id`,`name`,`pass`,`level`,`resource`,`disabled`,`lockedtime`,`lastsession`,`creator`) VALUES
(1,'admin',MD5('admin'),'sysadmin','1','N',0,'',''),
(2,'analyser',MD5('admin'),'analyser','1','N',0,'',''),
(3,'viewer',MD5('admin'),'viewer','1','N',0,'','');
SELECT id, name, level, resource FROM t_user;
EOF
echo ""
echo "=== 2. 测试 config type=user ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c /tmp/ly_cookie3.txt --max-time 30 >/dev/null
curl -s "http://127.0.0.1/d/config?type=user&op=get" -b /tmp/ly_cookie3.txt --max-time 60 2>&1 | head -c 800
echo ""
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
