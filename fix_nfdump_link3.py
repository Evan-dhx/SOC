import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Adding protobuf to nfdump LIBS ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Add -lprotobuf to LIBS
sed -i 's|LIBS = /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a|LIBS = -Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a|' Makefile

echo "Updated LIBS:"
grep '^LIBS' Makefile

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -15
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check all nfdump binaries ==="
ls -la /Agent/bin/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
