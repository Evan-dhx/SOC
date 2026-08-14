import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check build scripts
print("=== Checking std package scripts ===")
cmd = r"""
cd /root/SOC/ly_vis
cat packages/std/package.json | grep -A 20 '"scripts"'
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Build the std package (main frontend app)
print("\n=== Building @shadowflow/std ===")
cmd2 = r"""
cd /root/SOC/ly_vis
yarn std build 2>&1 | tail -30
echo ""
echo "Exit code: $?"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=600)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Check build output
print("\n=== Check build output ===")
cmd3 = r"""
ls -la /root/SOC/ly_vis/packages/std/build/ 2>/dev/null || ls -la /root/SOC/ly_vis/packages/std/dist/ 2>/dev/null
echo ""
du -sh /root/SOC/ly_vis/packages/std/build/ 2>/dev/null || du -sh /root/SOC/ly_vis/packages/std/dist/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode())

client.close()
