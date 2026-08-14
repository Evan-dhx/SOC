import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing permissions and reconfiguring nfdump ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Fix permissions
chmod +x configure missing compile install-sh

# Reconfigure
./configure --prefix=/Agent 2>&1 | tail -10
echo ""
echo "=== Building ==="
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check ==="
ls -la /Agent/bin/nf* 2>/dev/null
ls -la /Agent/bin/nfdump 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
