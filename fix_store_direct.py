import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the file
sftp = client.open_sftp()
with sftp.open('/root/SOC/ly_vis/packages/std/src/layout/components/config/store.js', 'r') as f:
    content = f.read().decode('utf-8')
sftp.close()

# Fix the line
old_line = "                obj[k] = d.slice().sort((a, b) => a.id - b.id)"
new_line = "                obj[k] = Array.isArray(d) ? d.slice().sort((a, b) => a.id - b.id) : []"

if old_line in content:
    content = content.replace(old_line, new_line)
    print("Line replaced successfully!")
else:
    print("ERROR: Could not find the line to replace!")
    print("Looking for:", repr(old_line))

# Write back
with sftp.open('/root/SOC/ly_vis/packages/std/src/layout/components/config/store.js', 'w') as f:
    f.write(content)
sftp.close()

# Verify
with sftp.open('/root/SOC/ly_vis/packages/std/src/layout/components/config/store.js', 'r') as f:
    new_content = f.read().decode('utf-8')
sftp.close()

print("\n=== Fixed lines 55-62 ===")
lines = new_content.split('\n')
for i in range(54, 62):
    print(f"{i+1}: {lines[i]}")

# Rebuild
print("\n=== Rebuilding ===")
cmd = r"""
cd /root/SOC/ly_vis
export NODE_OPTIONS=--openssl-legacy-provider
export CI=false
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false
yarn std build 2>&1 | tail -10
echo "Build: ${PIPESTATUS[0]}"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))

# Deploy
print("\n=== Deploying ===")
cmd2 = r"""
rm -rf /Server/www/ui/*
cp -r /root/SOC/ly_vis/packages/std/build/* /Server/www/ui/
echo "Deployed!"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
