import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing ALL shell scripts line endings ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Fix all shell scripts and text files with \r
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
find . -name "*.in" -exec sed -i 's/\r$//' {} \;
sed -i 's/\r$//' ylwrap missing compile install-sh configure config.h.in 2>/dev/null

# Make sure all scripts are executable
chmod +x ylwrap missing compile install-sh configure

echo "=== Rebuilding ==="
make 2>&1 | tail -30
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
