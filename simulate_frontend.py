import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Simulate exactly what the frontend sends
cmds = [
    # Test all the exact API calls the frontend makes
    ("simulate frontend calls", r"""
# Login first
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

# deviceApi - what overview page calls
echo "1. deviceApi (type=agent, target=device):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent&target=device" 2>&1 | head -c 300
echo ""

# proxyApi
echo "2. proxyApi (type=agent):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=agent" 2>&1 | head -c 300
echo ""

# moApi
echo "3. moApi (type=mo):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=mo" 2>&1 | head -c 300
echo ""

# mogroupApi (note: op=gget not op=get!)
echo "4. mogroupApi (type=mo_group, op=gget):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=gget&type=mo_group" 2>&1 | head -c 300
echo ""

# eventConfigApiConfig (type=event_config)
echo "5. eventConfig (type=event_config):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_config" 2>&1 | head -c 300
echo ""

# eventConfigApiType (type=event_type)
echo "6. eventType (type=event_type):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_type" 2>&1 | head -c 300
echo ""

# eventConfigApiLevel (type=event_level)
echo "7. eventLevel (type=event_level):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_level" 2>&1 | head -c 300
echo ""

# eventConfigApiAction (type=event_action)
echo "8. eventAction (type=event_action):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_action" 2>&1 | head -c 300
echo ""

# eventConfigApiIgnore (type=event_ignore)
echo "9. eventIgnore (type=event_ignore):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=event_ignore" 2>&1 | head -c 300
echo ""

# blacklistApi (type=bwlist, target=blacklist)
echo "10. blacklist (type=bwlist, target=blacklist):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=blacklist" 2>&1 | head -c 300
echo ""

# whitelistApi
echo "11. whitelist (type=bwlist, target=whitelist):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=bwlist&target=whitelist" 2>&1 | head -c 300
echo ""

# internalApi
echo "12. internalip (type=internalip):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=internalip" 2>&1 | head -c 300
echo ""

# userApi
echo "13. user (type=user):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 300
echo ""
"""),

    # Check error log
    ("errors", "tail -10 /var/log/httpd/ly_error_log"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
