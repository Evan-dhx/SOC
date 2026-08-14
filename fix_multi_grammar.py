import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing multi_grammar.y pointer comparison ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Check context around the errors
sed -n '1095,1102p' multi_grammar.y
echo "---"
sed -n '1166,1172p' multi_grammar.y

# Fix: s == '\0' -> *s == '\0' (pointer dereference)
sed -i "s|if ( s == '\\\\0' )|if ( *s == '\\\\0' )|g" multi_grammar.y

# Verify
echo "=== After fix ==="
grep -n "s == " multi_grammar.y | grep '\\0'

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -30
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
