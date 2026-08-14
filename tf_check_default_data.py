import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("全表数据量 + mo/config 逻辑", r"""
echo "=== 1. 所有表数据量 ==="
mysql -uroot -ppassword123 server -e "SHOW TABLES;" 2>&1 | tail -30
echo ""
echo "=== 2. t_mo 表 ==="
mysql -uroot -ppassword123 server -e "SHOW CREATE TABLE t_mo\G" 2>&1 | head -20
mysql -uroot -ppassword123 server -e "SELECT * FROM t_mo;" 2>&1 | head -10
echo ""
echo "=== 3. 各配置表数据量 ==="
mysql -uroot -ppassword123 server -e "SELECT 't_blacklist' t, COUNT(*) c FROM t_blacklist UNION ALL SELECT 't_event_config_sus', COUNT(*) FROM t_event_config_sus UNION ALL SELECT 't_event_config_dns', COUNT(*) FROM t_event_config_dns UNION ALL SELECT 't_event_config_dnstunnel', COUNT(*) FROM t_event_config_dnstunnel UNION ALL SELECT 't_event_config_port_scan', COUNT(*) FROM t_event_config_port_scan UNION ALL SELECT 't_event_config_ip_scan', COUNT(*) FROM t_event_config_ip_scan UNION ALL SELECT 't_event_config_srv', COUNT(*) FROM t_event_config_srv UNION ALL SELECT 't_event_config_threshold', COUNT(*) FROM t_event_config_threshold UNION ALL SELECT 't_event_config_dga', COUNT(*) FROM t_event_config_dga;" 2>&1
echo ""
echo "=== 4. config CGI 查询逻辑 ==="
grep -n "SELECT\|FROM\|t_" /root/SOC/ly_server_src/server/config.cpp | head -20
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
