import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check nfdump structure
print("=== nfdump directory structure ===")
cmd = r"""
ls /root/SOC/ly_analyser_src/nfdump/
echo ""
echo "=== Check if configure exists ==="
ls -la /root/SOC/ly_analyser_src/nfdump/configure 2>/dev/null
echo ""
echo "=== Check if already configured ==="
ls /root/SOC/ly_analyser_src/nfdump/Makefile | head -3
echo ""
echo "=== Check for autogen.sh ==="
ls /root/SOC/ly_analyser_src/nfdump/autogen.sh 2>/dev/null
echo ""
echo "=== Check nfdump subdirs ==="
ls /root/SOC/ly_analyser_src/nfdump/src/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Try to build nfdump
print("\n=== Building nfdump ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/nfdump

# Check if configure script exists, if not check for autogen
if [ ! -f configure ]; then
    echo "No configure script, checking for autogen..."
    ls *.ac *.am 2>/dev/null
fi

# Try make directly (might already be configured)
make 2>&1 | tail -20
echo ""
echo "Exit code: $?"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
