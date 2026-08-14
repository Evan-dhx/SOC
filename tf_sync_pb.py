import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
files = [
    (r'd:\QorderProject\SOC\ly_server\src\common\config.proto', '/root/SOC/ly_server_src/common/config.proto'),
    (r'd:\QorderProject\SOC\ly_server\src\lib\config_agent.proto', '/root/SOC/ly_server_src/lib/config_agent.proto'),
    (r'd:\QorderProject\SOC\ly_server\src\lib\config_agent.cpp', '/root/SOC/ly_server_src/lib/config_agent.cpp'),
    (r'd:\QorderProject\SOC\ly_server\src\server\config_pusher.cpp', '/root/SOC/ly_server_src/server/config_pusher.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\common\config.proto', '/root/SOC/ly_analyser_src/common/config.proto'),
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp', '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\fsd.cpp', '/root/SOC/ly_analyser_src/agent/handlers/fsd.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\nftls\nftls.c', '/root/SOC/ly_analyser_src/nftls/nftls.c'),
    (r'd:\QorderProject\SOC\ly_analyser\src\nftls\Makefile', '/root/SOC/ly_analyser_src/nftls/Makefile'),
]
for local, remote in files:
    try:
        sftp.put(local, remote)
        print(f"OK {remote}")
    except Exception as e:
        print(f"FAIL {remote}: {e}")
sftp.close()

cmds = [
    ("pb 重新生成（config.proto / config_agent.proto）", r"""
export LD_LIBRARY_PATH=/root/build_deps/protobuf-3.8.0/src/.libs
PROTOC=/root/build_deps/protobuf-3.8.0/src/protoc
echo "=== 1. ly_server common config.proto ==="
cd /root/SOC/ly_server_src/common
cp config.pb.cc /root/SOC/ly_server_src/common/pb_backup/config.pb.cc.$(date +%H%M%S) 2>/dev/null
cp config.pb.h /root/SOC/ly_server_src/common/pb_backup/config.pb.h.$(date +%H%M%S) 2>/dev/null
$PROTOC config.proto --cpp_out=. 2>&1 | head -5
ls -la config.pb.cc config.pb.h 2>/dev/null | head -2
echo ""
echo "=== 2. ly_server lib config_agent.proto ==="
cd /root/SOC/ly_server_src/lib
cp config_agent.pb.cc config_agent.pb.cc.bak 2>/dev/null
cp config_agent.pb.h config_agent.pb.h.bak 2>/dev/null
$PROTOC config_agent.proto --cpp_out=. 2>&1 | head -5
grep -c "set_psk" config_agent.pb.h 2>/dev/null
echo ""
echo "=== 3. ly_analyser common config.proto ==="
cd /root/SOC/ly_analyser_src/common
cp config.pb.cc /root/SOC/ly_analyser_src/common/pb_backup/config.pb.cc.$(date +%H%M%S) 2>/dev/null
cp config.pb.h /root/SOC/ly_analyser_src/common/pb_backup/config.pb.h.$(date +%H%M%S) 2>/dev/null
$PROTOC config.proto --cpp_out=. 2>&1 | head -5
grep -c "set_psk" config.pb.h 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()