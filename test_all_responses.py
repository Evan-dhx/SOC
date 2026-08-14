import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Test all the exact API calls the overview page makes and check response format
print("=== Full API response test ===")
cmd = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "=== 1. deviceApi (type=agent, target=device) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1
echo ""

echo ""
echo "=== 2. proxyApi (type=agent) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent" 2>&1
echo ""

echo ""
echo "=== 3. moApi (type=mo) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=mo" 2>&1
echo ""

echo ""
echo "=== 4. mogroupApi (type=mo_group, op=gget) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=gget&type=mo_group" 2>&1
echo ""

echo ""
echo "=== 5. eventConfig (type=event_config) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_config" 2>&1
echo ""

echo ""
echo "=== 6. eventType (type=event_type) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_type" 2>&1
echo ""

echo ""
echo "=== 7. eventLevel (type=event_level) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_level" 2>&1
echo ""

echo ""
echo "=== 8. eventAction (type=event_action) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1
echo ""

echo ""
echo "=== 9. eventIgnore (type=event_ignore) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1
echo ""

echo ""
echo "=== 10. blacklist (type=bwlist, target=blacklist) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1
echo ""

echo ""
echo "=== 11. whitelist (type=bwlist, target=whitelist) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=whitelist" 2>&1
echo ""

echo ""
echo "=== 12. internalip (type=internalip) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=internalip" 2>&1
echo ""

echo ""
echo "=== 13. user (type=user) ==="
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1
echo ""
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
print(out)

# Check error log
print("\n=== Error log ===")
cmd2 = r"""
tail -5 /var/log/httpd/ly_error_log
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
