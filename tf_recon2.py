import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("nfcapd 加密能力 + tsensor 源码检查", r"""
echo "=== 1. nfcapd 版本与帮助（加密相关） ==="
/Agent/bin/nfcapd -V 2>&1 | head -3
/Agent/bin/nfcapd -h 2>&1 | grep -iE "tls|psk|ssl|encrypt|-T|-E|key" | head -15
echo ""
echo "=== 2. nfcapd TLSP 相关字符串上下文 ==="
strings /Agent/bin/nfcapd 2>/dev/null | grep -B2 -A2 "TLSP" | head -20
echo ""
echo "=== 3. tsensor(lyprobe) 源码 export/collect 中 TLS 相关 ==="
grep -rniE "tls|psk|ssl_|SSL_|openssl" /root/tsensor/*.c /root/tsensor/*.h 2>/dev/null | grep -vE "\.deps|\.Po" | head -15
echo ""
echo "=== 4. lyprobe 版本 ==="
grep -m1 "VERSION" /root/tsensor/configure.in 2>/dev/null || grep -m2 "AC_INIT" /root/tsensor/configure.in 2>/dev/null
echo ""
echo "=== 5. t_agent 实际表名 ==="
mysql -uroot -ppassword123 server -e "SHOW TABLES;" 2>/dev/null | grep -iE "agent|device|node"
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