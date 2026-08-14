import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("部署 sctl/mo + 重编译 extract_event/logout/threatinfo", r"""
echo "=== 1. 部署新 sctl/mo ==="
cp /root/SOC/ly_server_src/server/sctl /Server/www/d/sctl
cp /root/SOC/ly_server_src/server/mo /Server/www/d/mo
chmod 755 /Server/www/d/sctl /Server/www/d/mo
echo "部署完成"
echo ""
echo "=== 2. 测试 sctl ==="
curl -s "http://127.0.0.1/d/sctl?op=get" --max-time 30 2>&1 | head -c 500
echo ""
echo "=== 3. 测试 mo（op=get 正确参数） ==="
curl -s "http://127.0.0.1/d/mo?op=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 800
echo ""
echo "=== 4. 重编译 extract_event ==="
cd /root/SOC/ly_analyser_src/agent/handlers
cp /Agent/cmd/extract_event /Agent/cmd/extract_event.bak_old 2>/dev/null
rm -f extract_event event_extractor.o event_filter.o extract_event.o
make extract_event 2>&1 | tail -5
echo ""
echo "=== 5. 重编译 extract_event_feature / extract_pcap ==="
cp /Agent/cmd/extract_event_feature /Agent/cmd/extract_event_feature.bak_old 2>/dev/null
cp /Agent/cmd/extract_pcap /Agent/cmd/extract_pcap.bak_old 2>/dev/null
rm -f extract_event_feature extract_pcap extract_event_feature.o extract_pcap.o
make extract_event_feature extract_pcap 2>&1 | tail -5
echo ""
echo "=== 6. 重编译 logout/threatinfo/threatinfopro ==="
cd /root/SOC/ly_server_src/server
rm -f logout threatinfo threatinfopro
make threatinfo threatinfopro 2>&1 | tail -3
ls /root/SOC/ly_server_src/server/logout 2>/dev/null || echo "logout 无 Makefile 目标，跳过"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
