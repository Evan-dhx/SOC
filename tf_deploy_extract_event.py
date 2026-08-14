import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("部署新二进制 + 测试 event", r"""
echo "=== 1. 部署 extract 系列 ==="
cp /root/SOC/ly_analyser_src/agent/handlers/extract_event /Agent/cmd/extract_event
cp /root/SOC/ly_analyser_src/agent/handlers/extract_event_feature /Agent/cmd/extract_event_feature
cp /root/SOC/ly_analyser_src/agent/handlers/extract_pcap /Agent/cmd/extract_pcap
chmod 755 /Agent/cmd/extract_event /Agent/cmd/extract_event_feature /Agent/cmd/extract_pcap
ls -la /Agent/cmd/extract_*
echo ""
echo "=== 2. 部署 threatinfo 系列 ==="
cp /root/SOC/ly_server_src/server/threatinfo /Server/www/d/threatinfo
cp /root/SOC/ly_server_src/server/threatinfopro /Server/www/d/threatinfopro
chmod 755 /Server/www/d/threatinfo /Server/www/d/threatinfopro
echo "部署完成"
echo ""
echo "=== 3. 测试 event 接口 ==="
curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 90 2>&1 | head -c 800
echo ""
echo ""
echo "=== 4. 测试 extract_event 直接调用 ==="
echo 'devid: 1' | timeout 60 /Agent/cmd/extract_event 2>&1 | head -c 500
echo ""
echo ""
echo "=== 5. 前端 sctl/logout 调用方式 ==="
grep -o ".\{50\}sctl.\{100\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -c 600
echo ""
grep -o ".\{50\}logout.\{100\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -c 400
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
