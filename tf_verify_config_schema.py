import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("代码查询列名验证", r"""
echo "=== 1. 代码中 t_event_config 查询 ==="
grep -rn "t_event_config_black\|t_event_config_dns\|t_event_config_sus" /root/SOC/ly_server_src /root/SOC/ly_analyser_src 2>/dev/null | grep -v "\.o:" | grep -iE "select|from" | head -10
echo ""
echo "=== 2. event_config 相关 SQL 上下文 ==="
grep -rn -B2 -A8 "FROM `t_event_config_black`\|FROM t_event_config_black" /root/SOC/ly_server_src/server/*.cpp /root/SOC/ly_analyser_src/common/*.cpp 2>/dev/null | head -40
echo ""
echo "=== 3. 现有表结构对比（black/dns/sus） ==="
mysql -uroot -ppassword123 server -e "SHOW CREATE TABLE t_event_config_black\G SHOW CREATE TABLE t_event_config_dns\G SHOW CREATE TABLE t_event_config_sus\G" 2>&1 | grep -E "Table:|^\s+\`|ENGINE" | head -40
echo ""
echo "=== 4. t_event_list/t_event_type/t_event_level 现有结构 ==="
mysql -uroot -ppassword123 server -e "SHOW CREATE TABLE t_event_list\G" 2>&1 | grep -E "^\s+\`|ENGINE" | head -20
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
