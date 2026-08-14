import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing nfdump Makefile link flags ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Check current LDFLAGS/LIBS
grep -n 'flow_filter\|tensorflow\|LDFLAGS\|LDADD\|LIBS' Makefile | head -20

echo ""
echo "=== Fixing ==="
# Remove -lflow_filter -lcommon -ltensorflow_cc -ltensorflow_framework from Makefile
sed -i 's|-lflow_filter||g' Makefile
sed -i 's|-ltensorflow_cc||g' Makefile
sed -i 's|-ltensorflow_framework||g' Makefile
# Keep -lcommon if it's needed, but check first
# Actually nfdump shouldn't need -lcommon either
sed -i 's|-lcommon||g' Makefile
# Remove -L/Agent/lib and -L/usr/local/lib if they were only for the above
sed -i 's|-L/Agent/lib||g' Makefile

echo "After fix:"
grep -n 'nfdump.*nfdump-nfdump' Makefile | head -5

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check nfdump binaries ==="
ls -la /Agent/bin/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
