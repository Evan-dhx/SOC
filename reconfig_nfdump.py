import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Reconfigure nfdump with correct paths
print("=== Reconfiguring nfdump ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Check configure.in for options
head -30 configure.in
echo ""
echo "=== Running configure ==="
./configure --prefix=/Agent 2>&1 | tail -20
echo ""
echo "=== Building nfdump ==="
make 2>&1 | tail -20
echo ""
echo "=== Installing nfdump ==="
make install 2>&1 | tail -20
echo ""
echo "=== Check nfdump binaries ==="
ls -la /Agent/bin/nf* 2>/dev/null
ls -la /Agent/bin/nfdump 2>/dev/null
which nfdump 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
