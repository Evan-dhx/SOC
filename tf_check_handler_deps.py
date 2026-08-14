import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check deps status", r"""
echo "=== 1. flow_filter_noai.a 是否存在 ==="
ls -lh /root/SOC/ly_analyser_src/agent/flow/flow_filter*.a 2>/dev/null
echo ""
echo "=== 2. utils.a ==="
ls -lh /root/SOC/ly_analyser_src/agent/utils/utils.a 2>/dev/null
echo ""
echo "=== 3. 各模块 .a 时间 ==="
ls -lh /root/SOC/ly_analyser_src/agent/config/config.a /root/SOC/ly_analyser_src/agent/model/model.a /root/SOC/ly_analyser_src/agent/data/data.a /root/SOC/ly_analyser_src/agent/dump/libnfdump.a 2>/dev/null
echo ""
echo "=== 4. 系统 protoc 版本 ==="
which protoc && protoc --version
echo ""
echo "=== 5. event.pb.cc 时间戳 ==="
ls -la /root/SOC/ly_analyser_src/agent/handlers/event.pb.* 2>/dev/null
echo ""
echo "=== 6. extractor.o 时间戳 ==="
ls -la /root/SOC/ly_analyser_src/agent/handlers/extractor.o /root/SOC/ly_analyser_src/agent/handlers/extractor 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
