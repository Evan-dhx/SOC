import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing ALL files with Windows line endings in nfdump ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Fix ALL files recursively - find files that contain \r
find . -type f -exec grep -Pl '\r' {} \; | while read f; do
    sed -i 's/\r$//' "$f"
    echo "Fixed: $f"
done

# Make scripts executable
chmod +x depcomp ylwrap missing compile install-sh configure 2>/dev/null

echo ""
echo "=== Reconfigure + Build ==="
./configure --prefix=/Agent 2>&1 | tail -5
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check nfdump ==="
ls -la /Agent/bin/nf* 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
