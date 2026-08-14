import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View define.h and extractor process", r"""
echo "=== 1. define.h 完整 ==="
cat /root/SOC/ly_analyser_src/agent/define.h
echo ""
echo "=== 2. extractor.cpp process() 完整 ==="
sed -n '/static void process/,/^static void usage/p' /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -80
"""),

    ("Manual indexer test", r"""
echo "=== 3. 手动运行 indexer（直接） ==="
cd /Agent/bin
ls -la /data/flow/*.nfcapd* 2>/dev/null | tail -4
echo ""
echo "--- 用最新有数据的文件 ---"
DEVID=1 STARTTIME=1786597800 ENDTIME=1786598100 timeout 60 ./indexer -r /data/flow/nfcapd.202608131334 2>&1 | head -20
echo "Indexer exit: $?"
echo ""
echo "=== 4. 检查是否生成 db 目录 ==="
find /Agent/data -type d 2>/dev/null
ls -la /Agent/data/db/ 2>/dev/null | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
