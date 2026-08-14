import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing grammar.y pointer comparison ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Fix s == '\0' -> *s == '\0' in grammar.y
sed -i "s|if ( s == '\\\\0' )|if ( *s == '\\\\0' )|g" grammar.y

# Verify
grep -n "s == " grammar.y | grep '\\0'

# Also need to regenerate grammar.c from grammar.y
# The Makefile should do this automatically via ylwrap/bison
# But let's remove the old grammar.c to force regeneration
rm -f grammar.c grammar.h

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check ==="
ls -la /Agent/bin/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
