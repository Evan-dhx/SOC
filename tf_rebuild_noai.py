import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重打包 flow_filter_noai.a 并重链 extract_feature", r"""
cd /root/SOC/ly_analyser_src/agent/flow
echo "=== 1. 备份旧归档 ==="
cp flow_filter_noai.a flow_filter_noai.a.bak_old
echo ""
echo "=== 2. 用新 .o 重新打包 ==="
ar rcs flow_filter_noai.a assetsrv_filter.o bw_filter.o dns_filter.o dns_tunnel.o flow_file_util.o flow_filter.o frn_trip_filter.o icmp_tunnel.o ip_scan_filter.o ip_set_filter.o mo_filter.o nf_scanner.o port_scan_filter.o service_filter.o tcpinit_filter.o threshold_filter.o url_content_filter.o
echo "打包完成:"
ar t flow_filter_noai.a | wc -l
ls -la flow_filter_noai.a
echo ""
echo "=== 3. 重链接 extract_feature ==="
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f extract_feature
make extract_feature 2>&1 | tail -10
echo ""
echo "=== 4. 检查产物 ==="
ls -la extract_feature 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
