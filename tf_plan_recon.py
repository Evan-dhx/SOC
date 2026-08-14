import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("lyprobe/tsensor 源码与接收端现状", r"""
echo "=== 1. lyprobe 源码位置 ==="
find /root /opt /home -maxdepth 3 -iname "*lyprobe*" -o -maxdepth 3 -iname "*tsensor*" 2>/dev/null | grep -v proc | head -10
echo ""
echo "=== 2. stunnel 可用性 ==="
which stunnel 2>&1; rpm -qa 2>/dev/null | grep -i stunnel | head -2
echo ""
echo "=== 3. 接收端 nfcapd 来源 ==="
ls -la /Agent/bin/nfcapd 2>/dev/null
strings /Agent/bin/nfcapd 2>/dev/null | grep -iE "tls|ssl|encrypt" | head -5
echo ""
echo "=== 4. 采集节点配置（t_config / agent 配置） ==="
mysql -uroot -ppassword123 server -e "SELECT id,name,ip,port,interface,pcap_level FROM t_agent LIMIT 5;" 2>/dev/null
echo ""
echo "=== 5. 服务器上的 nfdump 源码 ==="
ls /root/SOC/ly_analyser_src/nfdump/ 2>/dev/null | head -8
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()