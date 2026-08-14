import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Building with NODE_OPTIONS=--openssl-legacy-provider ===")
cmd = r"""
cd /root/SOC/ly_vis
export NODE_OPTIONS=--openssl-legacy-provider
yarn std build 2>&1 | tail -30
echo ""
echo "Exit code: $?"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Check build output
print("\n=== Check build output ===")
cmd2 = r"""
ls -la /root/SOC/ly_vis/packages/std/build/ 2>/dev/null
echo ""
du -sh /root/SOC/ly_vis/packages/std/build/ 2>/dev/null
echo ""
ls /root/SOC/ly_vis/packages/std/build/static/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode())

# Deploy to /Server/www/ui/
print("\n=== Deploying to /Server/www/ui/ ===")
cmd3 = r"""
# Copy build output to Server/www/ui
rm -rf /Server/www/ui/*
cp -r /root/SOC/ly_vis/packages/std/build/* /Server/www/ui/
echo "Deployed to /Server/www/ui/"
ls -la /Server/www/ui/
echo ""
du -sh /Server/www/ui/
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
