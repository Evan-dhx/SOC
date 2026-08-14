import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("dump 所有相关表结构", r"""
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
SHOW CREATE TABLE t_mo\G
SHOW CREATE TABLE t_event_config_dga\G
SHOW CREATE TABLE t_event_config_dnstunnel\G
SHOW CREATE TABLE t_event_config_icmp_tunnel\G
SHOW CREATE TABLE t_event_config_ip_scan\G
SHOW CREATE TABLE t_event_config_port_scan\G
SHOW CREATE TABLE t_event_config_srv\G
SHOW CREATE TABLE t_event_config_threshold\G
SHOW CREATE TABLE t_event_config_url_content\G
SHOW CREATE TABLE t_event_config_frn_trip\G
SHOW CREATE TABLE t_event_config_dnstun_ai\G
SHOW CREATE TABLE t_event_status\G
SHOW CREATE TABLE t_event_type\G
SHOW CREATE TABLE t_event_level\G
SHOW CREATE TABLE t_event_action\G
SHOW CREATE TABLE t_internal_ip_list\G
SHOW CREATE TABLE t_url_attack_type\G
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
