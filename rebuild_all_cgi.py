import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Rebuild ALL CGI binaries
    ("rebuild all", r"""
cd /root/SOC/ly_server_src/server
make clean 2>/dev/null
make 2>&1 | tail -20
echo "Build exit: ${PIPESTATUS[0]}"
"""),
    
    # Install ALL binaries
    ("install all", r"""
# Copy all CGI binaries
for bin in auth bwlist config event feature event_feature mo internalip sctl evidence locinfo geoinfo portinfo ipinfo threatinfo threatinfopro; do
    if [ -f /root/SOC/ly_server_src/server/$bin ]; then
        cp /root/SOC/ly_server_src/server/$bin /Server/www/d/$bin
        echo "Installed: $bin"
    fi
done

# Also copy config_pusher and gen_event to /Server/bin/
cp /root/SOC/ly_server_src/server/config_pusher /Server/bin/config_pusher 2>/dev/null
cp /root/SOC/ly_server_src/server/gen_event /Server/bin/gen_event 2>/dev/null
echo "Done"
ls -la /Server/www/d/
"""),
    
    # Test all endpoints
    ("test endpoints", r"""
echo "=== auth ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/auth -d "auth_target=login&user=admin&pass=admin"
echo ""
echo "=== config ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/config
echo ""
echo "=== event ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/event
echo ""
echo "=== feature ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/feature
echo ""
echo "=== bwlist ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost/d/bwlist
echo ""
"""),
    
    # Check error log
    ("error log", "tail -5 /var/log/httpd/ly_error_log"),
    
    # Test from browser perspective - full page load
    ("full page test", r"""
curl -s http://localhost/ui/ 2>/dev/null | grep -o '<title>.*</title>'
echo "---"
curl -s -o /dev/null -w "UI: %{http_code}\n" http://localhost/ui/
curl -s -o /dev/null -w "Auth: %{http_code}\n" http://localhost/d/auth -d "auth_target=login&user=admin&pass=admin"
curl -s -o /dev/null -w "Config: %{http_code}\n" http://localhost/d/config
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
