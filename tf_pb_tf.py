import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("TF protoc 3.21.9 重新生成 pb + 编译", r"""
export LD_LIBRARY_PATH=/root/tensorflow/bazel-bin/external/com_google_protobuf
PROTOC=/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc
echo "=== 1. ly_analyser common config.proto ==="
cd /root/SOC/ly_analyser_src/common
$PROTOC config.proto --cpp_out=. 2>&1 | head -5
grep -c "set_psk" config.pb.h
echo ""
echo "=== 2. ly_server common config.proto ==="
cd /root/SOC/ly_server_src/common
$PROTOC config.proto --cpp_out=. 2>&1 | head -5
grep -c "set_psk" config.pb.h
echo ""
echo "=== 3. ly_server lib config_agent.proto ==="
cd /root/SOC/ly_server_src/lib
$PROTOC config_agent.proto --cpp_out=. 2>&1 | head -5
grep -c "set_psk" config_agent.pb.h
echo ""
echo "=== 4. 编译 agent actl + fsd ==="
cd /root/SOC/ly_analyser_src/agent/handlers
make actl 2>&1 | tail -4
make fsd 2>&1 | tail -4
ls -la actl fsd 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n{'='*20} {label} {'='*20}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()