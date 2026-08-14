import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Batch fix includes and rebuild all", r"""
echo "=== 1. 批量修改 include 指向新 common ==="
cd /root/SOC/ly_server_src/server
for f in *.cpp; do
  sed -i 's|#include "../common/|#include "../../ly_analyser_src/common/|' "$f"
done
echo "批量替换完成"
echo ""
echo "=== 2. 检查 Makefile install 规则 ==="
grep -n -A10 "^install:" /root/SOC/ly_server_src/server/Makefile | head -15
echo ""
echo "=== 3. 清理旧对象并全量编译 ==="
rm -f *.o config_pusher gen_event
make 2>&1 | tail -15
echo "Make exit: $?"
ls -la config_pusher gen_event mo internalip event bwlist feature event_feature locinfo geoinfo portinfo ipinfo config auth sctl evidence 2>/dev/null | awk '{print $5, $9}' | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
