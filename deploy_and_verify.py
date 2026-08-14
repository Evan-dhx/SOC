import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Deploy to /Server/www/ui/
print("=== Deploying frontend to /Server/www/ui/ ===")
cmd = r"""
rm -rf /Server/www/ui/*
cp -r /root/SOC/ly_vis/packages/std/build/* /Server/www/ui/
chmod -R 755 /Server/www/ui/
echo "Deployed!"
ls -la /Server/www/ui/
echo ""
du -sh /Server/www/ui/
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# Restart httpd to pick up changes
print("\n=== Restarting httpd ===")
cmd2 = r"""
systemctl restart httpd
systemctl status httpd | head -5
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# ============================================================
# Phase 12: Full verification
# ============================================================
print("\n" + "=" * 60)
print("PHASE 12: FULL VERIFICATION")
print("=" * 60)

cmd3 = r"""
echo "=== 1. Service Status ==="
echo "httpd: $(systemctl is-active httpd)"
echo "mariadb: $(systemctl is-active mariadb)"
echo "crond: $(systemctl is-active crond)"
echo "firewalld: $(systemctl is-active firewalld)"
echo "chronyd: $(systemctl is-active chronyd)"

echo ""
echo "=== 2. Agent Binaries ==="
ls -la /Agent/bin/
echo ""
echo "Agent CMD:"
ls -la /Agent/cmd/
echo ""
echo "Agent LIB:"
ls -la /Agent/lib/
echo ""
echo "Agent DATA:"
ls -la /Agent/data/

echo ""
echo "=== 3. Server Binaries ==="
ls -la /Server/bin/
echo ""
echo "Server CGI:"
ls -la /Server/www/d/

echo ""
echo "=== 4. Frontend ==="
ls -la /Server/www/ui/
echo ""
echo "UI index.html exists: $(test -f /Server/www/ui/index.html && echo YES || echo NO)"

echo ""
echo "=== 5. Database ==="
mysql -u root -e "SHOW DATABASES;" 2>/dev/null

echo ""
echo "=== 6. Firewall ==="
firewall-cmd --list-services 2>/dev/null
firewall-cmd --list-ports 2>/dev/null

echo ""
echo "=== 7. HTTP Test ==="
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost/ui/ 2>/dev/null
echo ""
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost/d/ 2>/dev/null
echo ""

echo ""
echo "=== 8. Cron Jobs ==="
cat /etc/cron.d/ly_agent 2>/dev/null

echo ""
echo "=== 9. Library paths ==="
ldconfig -p | grep -E 'common|protobuf|cgicc|cppdb|tensorflow' 2>/dev/null | head -10

echo ""
echo "=== VERIFICATION COMPLETE ==="
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"STDERR: {err}")

client.close()
