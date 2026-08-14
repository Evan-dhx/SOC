import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check current indexing Makefile", r"""
echo "=== Current indexing Makefile ==="
cat /root/SOC/ly_analyser_src/agent/indexing/Makefile
"""),

    ("Update indexing Makefile INCS", r"""
echo "=== Update indexing Makefile ==="
cd /root/SOC/ly_analyser_src/agent/indexing

# 备份
cp Makefile Makefile.backup.2 2>/dev/null

# 更新 INCS 为与 flow/Makefile 相同的完整路径
sed -i 's|^INCS=.*|INCS=-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/third_party/eigen3 -I/usr/local/include/tf/tensorflow/core/protobuf -I/usr/local/include/tf/nsync_public -I/usr/local/include|' Makefile

echo "New INCS:"
grep "^INCS=" Makefile
echo ""
echo "New CXXFLAGS:"
grep "^CXXFLAGS=" Makefile
"""),

    ("Compile indexer", r"""
echo "=== Compile indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -60
echo ""
echo "Exit code: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer generated" || echo "FAIL: indexer not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
