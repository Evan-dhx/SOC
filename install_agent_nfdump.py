import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# ============================================================
# Step 1: Install agent binaries
# ============================================================
print("=== Installing agent modules ===")
cmd = r"""
# Create agent directories if not exist
mkdir -p /Agent/bin /Agent/cmd /Agent/lib /Agent/data

# Install indexer
cd /root/SOC/ly_analyser_src/agent/indexing
make install 2>&1
echo "Indexer installed"

# Install handlers
cd /root/SOC/ly_analyser_src/agent/handlers
make install 2>&1
echo "Handlers installed"

# Install common library
cp /root/SOC/ly_analyser_src/common/libcommon.so /Agent/lib/
echo "Common lib installed"

# Copy config files if any
ls /root/SOC/ly_analyser_src/agent/config/*.conf 2>/dev/null && cp /root/SOC/ly_analyser_src/agent/config/*.conf /Agent/data/ 2>/dev/null
ls /root/SOC/ly_analyser_src/agent/config/*.ini 2>/dev/null && cp /root/SOC/ly_analyser_src/agent/config/*.ini /Agent/data/ 2>/dev/null

echo "=== Agent installation summary ==="
echo "Agent bin:"
ls -la /Agent/bin/
echo ""
echo "Agent cmd:"
ls -la /Agent/cmd/
echo ""
echo "Agent lib:"
ls -la /Agent/lib/
echo ""
echo "Agent data:"
ls -la /Agent/data/
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Step 2: Check nfdump source and build
# ============================================================
print("\n=== Checking nfdump ===")
cmd2 = r"""
ls /root/SOC/ly_analyser_src/nfdump/
echo ""
cat /root/SOC/ly_analyser_src/nfdump/Makefile
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode())

client.close()
