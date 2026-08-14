import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Add -lprotobuf back and rebuild", r"""
echo "=== 1. 加回 -lprotobuf ==="
cd /root/SOC/ly_analyser_src/agent/handlers
sed -i 's/LDLIBS+=-lcommon -lcgicc/LDLIBS+=-lprotobuf -lcommon -lcgicc/' Makefile
grep "LDLIBS+=" Makefile | head -2
echo ""
echo "=== 2. 重编 extractor ==="
rm -f extractor.o extractor
make extractor 2>&1 | tail -8
echo ""
echo "Exit: $?"
ls -lh extractor 2>/dev/null && echo "OK: extractor built" || echo "FAIL"
"""),

    ("Test extractor", r"""
echo "=== 3. 测试 extractor ==="
cd /Agent/bin
cp /root/SOC/ly_analyser_src/agent/handlers/extractor .
now=$(date +"%s")
aligned=$[$now-$now%300-300]
timeout 30 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -30
echo "Exit: $?"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
