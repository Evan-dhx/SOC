import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing grammar.y compilation ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Add -Wno-write-strings to CFLAGS in Makefile
sed -i 's|nfdump_CFLAGS = -I/root/SOC/ly_analyser_src/agent -I/root/SOC/ly_analyser_src/common|nfdump_CFLAGS = -I/root/SOC/ly_analyser_src/agent -I/root/SOC/ly_analyser_src/common -Wno-write-strings|' Makefile

# Also add to the general CFLAGS
sed -i 's|CFLAGS = -g -O2 -Wall|CFLAGS = -g -O2 -Wall -Wno-write-strings|' Makefile

# Check what the full error is - let's see all errors from grammar
echo "=== Check grammar.y yyerror signature ==="
grep -n 'yyerror' grammar.y | head -5
echo ""

# Also fix the yyerror function to accept const char*
# Check if yyerror is defined in the .y file
grep -n 'void yyerror\|int yyerror' grammar.y | head -5

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
