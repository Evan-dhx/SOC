import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the request-config module to understand how requests are made
print("=== request-config source ===")
cmd = r"""
find /root/SOC/ly_vis/packages/components/ -name 'request-config*' -type f 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
files = stdout.read().decode('utf-8', errors='replace').strip()
print(files)

if files:
    for f in files.split('\n'):
        if f.strip() and ('.js' in f or '.jsx' in f):
            print(f"\n--- {f.strip()} ---")
            cmd2 = f"cat -n '{f.strip()}' 2>/dev/null | head -100"
            stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
            print(stdout.read().decode('utf-8', errors='replace'))

# Check how the frontend sends requests - look for the actual POST data format
print("\n=== Check built JS for request format ===")
cmd3 = r"""
# Search for how config requests are made in the built JS
grep -o 'auth_target=[^,}]*' /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | sort -u | head -20
echo "---"
grep -o 'type:[^,}]*' /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | grep -i 'agent\|device\|mo\|event' | sort -u | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test with the exact format the frontend might use
print("\n=== Test with different formats ===")
cmd4 = r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

# Test 1: with auth_target=config
echo "Test 1 (auth_target=config, type=agent):"
curl -s -b /tmp/cookies http://localhost/d/config -d "auth_target=config&type=agent&op=get" 2>&1 | head -c 100
echo ""

# Test 2: without auth_target
echo "Test 2 (no auth_target, type=agent):"
curl -s -b /tmp/cookies http://localhost/d/config -d "type=agent&op=get" 2>&1 | head -c 100
echo ""

# Test 3: check if session is required
echo "Test 3 (no session, type=agent):"
curl -s http://localhost/d/config -d "type=agent&op=get" 2>&1 | head -c 100
echo ""

# Test 4: device with auth_target
echo "Test 4 (auth_target=config, type=agent, target=device):"
curl -s -b /tmp/cookies http://localhost/d/config -d "auth_target=config&type=agent&target=device&op=get" 2>&1 | head -c 200
echo ""
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
