import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("对比官方 vs 现有表清单", r"""
echo "=== 1. 服务器现有全部表 ==="
mysql -uroot -ppassword123 server -e "SHOW TABLES;" 2>&1 | tail -40
echo ""
echo "=== 2. 官方 SQL 中的表 ==="
grep -o "CREATE TABLE \`[a-z_]*\`" /root/SOC/ly_server_src/../tf_extract_db/db.server.v1.1.231123/db.server.v1.1.231123.opensource.sql 2>/dev/null || echo "本地文件不在服务器，用已导入的表对比"
echo ""
echo "=== 3. 各表行数统计 ==="
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
SELECT 't_agent' t, COUNT(*) c FROM t_agent UNION ALL
SELECT 't_config', COUNT(*) FROM t_config UNION ALL
SELECT 't_device', COUNT(*) FROM t_device UNION ALL
SELECT 't_mo', COUNT(*) FROM t_mo UNION ALL
SELECT 't_mogroup', COUNT(*) FROM t_mogroup UNION ALL
SELECT 't_event_list', COUNT(*) FROM t_event_list UNION ALL
SELECT 't_event_type', COUNT(*) FROM t_event_type UNION ALL
SELECT 't_event_status', COUNT(*) FROM t_event_status UNION ALL
SELECT 't_event_level', COUNT(*) FROM t_event_level UNION ALL
SELECT 't_event_action', COUNT(*) FROM t_event_action UNION ALL
SELECT 't_event_data', COUNT(*) FROM t_event_data UNION ALL
SELECT 't_event_data_aggre', COUNT(*) FROM t_event_data_aggre UNION ALL
SELECT 't_event_ignore', COUNT(*) FROM t_event_ignore UNION ALL
SELECT 't_internal_ip_list', COUNT(*) FROM t_internal_ip_list UNION ALL
SELECT 't_internal_srv_list', COUNT(*) FROM t_internal_srv_list UNION ALL
SELECT 't_url_attack_type', COUNT(*) FROM t_url_attack_type UNION ALL
SELECT 't_blacklist', COUNT(*) FROM t_blacklist UNION ALL
SELECT 't_whitelist', COUNT(*) FROM t_whitelist UNION ALL
SELECT 't_user', COUNT(*) FROM t_user UNION ALL
SELECT 't_user_session', COUNT(*) FROM t_user_session UNION ALL
SELECT 't_user_session_history', COUNT(*) FROM t_user_session_history;
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
