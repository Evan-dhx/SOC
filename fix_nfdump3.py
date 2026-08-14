import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing line endings and reconfiguring nfdump ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Fix Windows line endings in all shell scripts
for f in configure missing compile install-sh; do
    if [ -f "$f" ]; then
        sed -i 's/\r$//' "$f"
        chmod +x "$f"
        echo "Fixed $f"
    fi
done

# Also fix Makefile.in files
find . -name "Makefile.in" -exec sed -i 's|\$(top_srcdir)/missing|/root/SOC/ly_analyser_src/nfdump/missing|g' {} \;
find . -name "Makefile.in" -exec sed -i 's|/root/analyse/nfdump|/root/SOC/ly_analyser_src/nfdump|g' {} \;

# Fix current Makefile too
sed -i 's|/root/analyse/nfdump|/root/SOC/ly_analyser_src/nfdump|g' Makefile

# Now reconfigure
echo "=== Running configure ==="
./configure --prefix=/Agent 2>&1 | tail -15
echo ""
echo "=== Building ==="
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check nfdump binaries ==="
ls -la /Agent/bin/nf* 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
