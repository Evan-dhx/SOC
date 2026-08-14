import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("pusher SQL 核对 + 手动执行", r"""
echo "=== 1. pusher 源码 SELECT 与 res >> ==="
sed -n '960,1000p' /root/SOC/ly_server_src/server/config_pusher.cpp
echo ""
echo "=== 2. 手动执行同一 SQL ==="
mysql -uroot -ppassword123 server -e "select t1.id, t1.name, t1.type, t2.id, t2.ip, t1.ip, t1.port, t1.disabled, t1.flowtype, t1.model, t1.pcap_level, t1.template, t1.filter, t1.interface, t1.tls_psk from t_device t1 join t_agent t2 on t1.agentid = t2.id;" 2>&1 | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()