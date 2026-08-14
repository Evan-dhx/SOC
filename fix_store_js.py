import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix the changeData method to handle non-array values
print("=== Patching store.js ===")
cmd = r"""
cd /root/SOC/ly_vis/packages/std/src/layout/components/config

# Backup
cp store.js store.js.orig

# Fix line 58: add Array.isArray check
sed -i 's|obj\[k\] = d.slice().sort((a, b) => a.id - b.id)|obj[k] = Array.isArray(d) ? d.slice().sort((a, b) => a.id - b.id) : (d || [])|' store.js

echo "Diff:"
diff store.js.orig store.js

echo ""
echo "Fixed line 58:"
sed -n '55,62p' store.js
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Rebuild frontend
print("\n=== Rebuilding frontend ===")
cmd2 = r"""
cd /root/SOC/ly_vis
export NODE_OPTIONS=--openssl-legacy-provider
export CI=false
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false

# Fix line endings first
find packages/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's/\r$//' {} \; 2>/dev/null

yarn std build 2>&1 | tail -10
echo "Build exit: ${PIPESTATUS[0]}"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))

# Deploy
print("\n=== Deploying ===")
cmd3 = r"""
rm -rf /Server/www/ui/*
cp -r /root/SOC/ly_vis/packages/std/build/* /Server/www/ui/
echo "Deployed to /Server/www/ui/"
ls /Server/www/ui/ | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
