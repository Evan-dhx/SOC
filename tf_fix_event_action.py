import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("修正 t_event_action + 验证", r"""
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
INSERT INTO `t_event_action`(`id`,`act`,`mail`,`phone`,`uid`,`desc`) VALUES (1,1,'mailname@mailservername.com','',NULL,'Admin mail');
SELECT 't_mo' t, COUNT(*) c FROM t_mo UNION ALL SELECT 't_mogroup', COUNT(*) FROM t_mogroup UNION ALL SELECT 't_event_type', COUNT(*) FROM t_event_type UNION ALL SELECT 't_event_list', COUNT(*) FROM t_event_list UNION ALL SELECT 't_event_status', COUNT(*) FROM t_event_status UNION ALL SELECT 't_event_level', COUNT(*) FROM t_event_level UNION ALL SELECT 't_event_action', COUNT(*) FROM t_event_action UNION ALL SELECT 't_event_config_black', COUNT(*) FROM t_event_config_black UNION ALL SELECT 't_event_config_sus', COUNT(*) FROM t_event_config_sus UNION ALL SELECT 't_event_config_dga', COUNT(*) FROM t_event_config_dga UNION ALL SELECT 't_event_config_dns', COUNT(*) FROM t_event_config_dns UNION ALL SELECT 't_event_config_dnstunnel', COUNT(*) FROM t_event_config_dnstunnel UNION ALL SELECT 't_event_config_icmp_tunnel', COUNT(*) FROM t_event_config_icmp_tunnel UNION ALL SELECT 't_event_config_ip_scan', COUNT(*) FROM t_event_config_ip_scan UNION ALL SELECT 't_event_config_port_scan', COUNT(*) FROM t_event_config_port_scan UNION ALL SELECT 't_event_config_srv', COUNT(*) FROM t_event_config_srv UNION ALL SELECT 't_url_attack_type', COUNT(*) FROM t_url_attack_type UNION ALL SELECT 't_internal_ip_list', COUNT(*) FROM t_internal_ip_list;
EOF
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
