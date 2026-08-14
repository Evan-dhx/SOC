import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("插件符号检查", r"""
echo "=== 1. ldd -r 检查未解析符号 ==="
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/lib/config_event.so 2>&1 | grep -i "undefined\|not found" | head -10
echo "--- config_mo ---"
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/lib/config_mo.so 2>&1 | grep -i "undefined\|not found" | head -5
echo "--- config_user ---"
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/lib/config_user.so 2>&1 | grep -i "undefined\|not found" | head -5
echo "--- config_agent ---"
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/lib/config_agent.so 2>&1 | grep -i "undefined\|not found" | head -5
echo ""
echo "=== 2. ly_error_log 完整尾部 8 行 ==="
tail -8 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 3. lib 目录 .pb.cc 生成时间 ==="
ls -la /root/SOC/ly_server_src/lib/*.pb.cc /root/SOC/ly_server_src/lib/*.pb.h 2>/dev/null | head -10
echo ""
echo "=== 4. 系统 protoc 版本 ==="
protoc --version 2>&1
/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc --version 2>&1
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
