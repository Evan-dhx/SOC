import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix SSL and install deps
print("=== Fixing SSL and installing deps ===")
cmd = r"""
cd /root/SOC/ly_vis

# Disable strict SSL for yarn
yarn config set strict-ssl false
npm config set strict-ssl false

# Also try with registry that works
yarn config set registry https://registry.npmmirror.com

# Install
yarn install --network-timeout 100000 2>&1 | tail -30
echo ""
echo "Exit code: $?"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Check workspace packages
print("\n=== Checking workspace packages ===")
cmd2 = r"""
cd /root/SOC/ly_vis
ls -la packages/
echo ""
for d in packages/*/; do
    echo "--- $d ---"
    cat "$d/package.json" 2>/dev/null | head -15
    echo ""
done
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

client.close()
