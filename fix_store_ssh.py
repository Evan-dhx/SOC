import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Use Python on the server to fix the file
print("=== Fixing store.js on server ===")
cmd = r"""
python3 -c "
import re
f = '/root/SOC/ly_vis/packages/std/src/layout/components/config/store.js'
with open(f, 'r') as fh:
    content = fh.read()
old = 'obj[k] = d.slice().sort((a, b) => a.id - b.id)'
new = 'obj[k] = Array.isArray(d) ? d.slice().sort((a, b) => a.id - b.id) : []'
content = content.replace(old, new)
with open(f, 'w') as fh:
    fh.write(content)
print('Fixed!')
"
echo "---"
sed -n '55,62p' /root/SOC/ly_vis/packages/std/src/layout/components/config/store.js
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Rebuild
print("\n=== Rebuilding ===")
cmd2 = r"""
cd /root/SOC/ly_vis
export NODE_OPTIONS=--openssl-legacy-provider
export CI=false
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false
yarn std build 2>&1 | tail -10
echo "Build: ${PIPESTATUS[0]}"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))

# Deploy
print("\n=== Deploying ===")
cmd3 = r"""
rm -rf /Server/www/ui/*
cp -r /root/SOC/ly_vis/packages/std/build/* /Server/www/ui/
echo "Deployed!"
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
