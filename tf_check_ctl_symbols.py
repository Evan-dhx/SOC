import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("ctl.pb 符号细节", r"""
echo "=== 1. sctl 未定义符号（ctl 相关） ==="
nm -u /Server/www/d/sctl 2>/dev/null | grep -i "ctl\|default" | head -10
echo ""
echo "=== 2. ctl.pb.cc 中 _i_give_permission 定义 ==="
grep -n "_i_give_permission" /root/SOC/ly_analyser_src/common/ctl.pb.cc | head -10
echo ""
echo "=== 3. ctl.pb.h 中 _i_give_permission 声明 ==="
grep -n "_i_give_permission" /root/SOC/ly_analyser_src/common/ctl.pb.h | head -10
echo ""
echo "=== 4. ctl.proto id 字段 ==="
grep -n -B3 -A5 "id\b" /root/SOC/ly_analyser_src/common/ctl.proto | head -30
echo ""
echo "=== 5. libcommon.so 中该符号定义方式 ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep "i_give_permission" | head -5
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
