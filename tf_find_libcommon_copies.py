import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("libcommon 副本 + ldd + validate_request", r"""
echo "=== 1. 所有 libcommon.so 副本 ==="
find / -name "libcommon.so*" 2>/dev/null | while read f; do echo "$f: $(md5sum $f | cut -d' ' -f1)"; done
echo ""
echo "=== 2. ldd sctl ==="
ldd /Server/www/d/sctl 2>&1 | grep -E "common|protobuf"
echo ""
echo "=== 3. 各副本是否含旧符号 CtlReq49 ==="
for f in $(find / -name "libcommon.so*" 2>/dev/null); do
  echo -n "$f: "
  nm -D "$f" 2>/dev/null | grep -c "give_permission_to_break_this_code_default_id_B5" || echo "0"
done
echo ""
echo "=== 4. validate_request 定义 ==="
grep -n -B2 -A30 "static bool validate_request" /root/SOC/ly_server_src/server/mo.cpp | head -50
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
