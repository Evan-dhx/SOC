import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("protobuf 运行时版本修复排查", r"""
echo "=== 1. .bak.old 与 /tmp/protobuf_build 版本核对 ==="
md5sum /usr/local/lib/libprotobuf.so.19.0.0.bak.old /tmp/protobuf_build/libprotobuf.so.3.21.9.0 /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null
echo ""
echo "=== 2. /tmp/protobuf_build 文件列表 ==="
ls -la /tmp/protobuf_build/ 2>/dev/null | head -15
echo ""
echo "=== 3. 当前库的 protobuf 版本标识 ==="
strings /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep -m2 "3\.[0-9]\+\.[0-9]\+"
echo "--- bak.old ---"
strings /usr/local/lib/libprotobuf.so.19.0.0.bak.old 2>/dev/null | grep -m2 "3\.[0-9]\+\.[0-9]\+"
echo ""
echo "=== 4. indexer 等二进制的 protobuf 依赖 ==="
ldd /home/Agent/bin/indexer 2>/dev/null | grep proto
ldd /home/Server/bin/config_pusher 2>/dev/null | grep proto
echo ""
echo "=== 5. 其他二进制是否也受影响（测试一个老二进制） ==="
/home/Server/bin/gen_event 2>&1 | head -2 || echo "gen_event 崩溃"
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