import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("flow/Makefile 完整", r"""
echo "=== flow/Makefile 全部 ==="
cat /root/SOC/ly_analyser_src/agent/flow/Makefile
echo ""
echo "=== flow_filter_noai.a 对象的编译时间 ==="
ls -la /root/SOC/ly_analyser_src/agent/flow/*.o 2>/dev/null | awk '{print $6, $7, $8, $9}' | head -30
echo ""
echo "=== common 头文件时间 ==="
ls -la /root/SOC/ly_analyser_src/common/feature.pb.h /root/SOC/ly_analyser_src/common/event.pb.h 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
