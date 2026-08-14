import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("protoc 验证 + 目录结构", r"""
echo "=== 1. build_deps protoc ==="
ls -la /root/build_deps/protobuf-3.8.0/src/protoc 2>/dev/null
LD_LIBRARY_PATH=/root/build_deps/protobuf-3.8.0/src/.libs /root/build_deps/protobuf-3.8.0/src/protoc --version 2>&1 | head -2
echo ""
echo "=== 2. /Agent /Server 符号链接 ==="
ls -la / | grep -E "^l.*Agent|^l.*Server"
echo ""
echo "=== 3. 现有 config.pb.cc 位置 ==="
find /root/SOC -name "config.pb.cc" 2>/dev/null | head -3
find /home -name "config.pb.cc" 2>/dev/null | head -3
echo ""
echo "=== 4. ly_server 编译产物位置 ==="
ls /home/Server/bin/ 2>/dev/null | head -10
ls /home/Server/lib/ 2>/dev/null | grep -E "config|\.so" | head -10
echo ""
echo "=== 5. ly_server Makefile 编译 config_agent ==="
grep -B2 -A5 "config_agent" /root/SOC/ly_server_src/lib/Makefile 2>/dev/null | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()