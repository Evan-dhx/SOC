import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 后台启动全量重编
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f *.o actl fsd config_updater extractor extract_event extract_event_feature extract_feature extract_pcap flow_scan output_unqlite
nohup make all > /tmp/rebuild_all.log 2>&1 &
echo "handlers 重编已启动"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
client.close()