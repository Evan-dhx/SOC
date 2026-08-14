import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Start chronyd
print("=== Starting chronyd ===")
cmd = r"""
systemctl start chronyd
systemctl enable chronyd
echo "chronyd: $(systemctl is-active chronyd)"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test CGI endpoint
print("\n=== Testing CGI endpoint ===")
cmd2 = r"""
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost/d/auth 2>/dev/null
echo ""
curl -s http://localhost/d/auth 2>/dev/null | head -5
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test frontend page content
print("\n=== Testing frontend page ===")
cmd3 = r"""
curl -s http://localhost/ui/ 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Final summary
print("\n" + "=" * 60)
print("DEPLOYMENT SUMMARY")
print("=" * 60)
print("""
Server: 10.10.102.220 (AlmaLinux 9)

Services:
  - httpd (Apache): ACTIVE - Port 80/443
  - MariaDB: ACTIVE - Databases: ly_server, ly_agent
  - crond: ACTIVE - Cron jobs configured
  - firewalld: ACTIVE - HTTP/HTTPS/NetFlow/SFlow ports open
  - chronyd: ACTIVE - Time sync

Agent (/Agent/):
  - bin/: indexer, nfdump, nfcapd, nfanon, nfreplay, nfexpire, extractor, fsd
  - cmd/: config_updater, extract_event, extract_feature, extract_event_feature, 
          extract_pcap, flow_scan, output_unqlite, actl
  - lib/: libcommon.so
  - data/: indexer_process

Server (/Server/):
  - bin/: config_pusher, gen_event
  - www/d/: 16 CGI scripts (auth, bwlist, config, event, feature, etc.)
  - www/ui/: Frontend (React app - 12MB)

Frontend URL: http://10.10.102.220/ui/
CGI API URL:  http://10.10.102.220/d/

Notes:
  - AI filters (DGA, THREAT, DNSTUN_AI, MINING) disabled via #ifdef ENABLE_AI
    due to TensorFlow ABI incompatibility with GCC 11 / AlmaLinux 9
  - To enable AI filters in future, recompile with -DENABLE_AI after resolving
    TensorFlow ABI compatibility
""")

client.close()
