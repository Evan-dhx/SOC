import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Start background monitor on server
stdin, stdout, stderr = client.exec_command(r"""
echo "=== 监控 nfcapd.current 30 秒 ==="
for i in $(seq 1 6); do
  stat -c "$(date +%H:%M:%S) %s bytes" /data/flow/nfcapd.current
  sleep 5
done
""", timeout=60)
print("[服务器监控已启动]")

# Generate traffic from Windows to server web (goes through ens192!)
print("\n[从 Windows 制造流量访问 http://10.10.102.220/ ]")
import urllib.request
ok = 0
for i in range(30):
    try:
        r = urllib.request.urlopen('http://10.10.102.220/', timeout=5)
        r.read()
        ok += 1
    except Exception as e:
        print(f"  req {i}: {e}")
    time.sleep(0.3)
print(f"成功 {ok}/30 次请求")

# Wait for monitor to finish
out = stdout.read().decode('utf-8', errors='replace')
print(out)

# Final check
stdin, stdout, stderr = client.exec_command("stat -c '%s bytes %y' /data/flow/nfcapd.current; ls -la /data/flow/ | tail -5", timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
