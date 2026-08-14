import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("protobuf 版本排查", r"""
echo "=== 1. 旧 config.pb.h 是否用 SetAllocatedNoArena ==="
grep -c "SetAllocatedNoArena" /root/SOC/ly_analyser_src/common/pb_backup/config.pb.h 2>/dev/null
grep -c "SetAllocatedNoArena" /root/SOC/ly_analyser_src/common/config.pb.h.bak 2>/dev/null || true
echo ""
echo "=== 2. TF protoc ==="
ls -la /root/tensorflow/bazel-bin/external/com_google_protobuf/protoc 2>/dev/null
LD_LIBRARY_PATH=/root/tensorflow/bazel-bin/external/com_google_protobuf /root/tensorflow/bazel-bin/external/com_google_protobuf/protoc --version 2>&1 | head -2
echo ""
echo "=== 3. 编译用的 protobuf 头文件版本 ==="
grep -m1 "PROTOBUF_VERSION" /usr/local/include/google/protobuf/stubs/common.h 2>/dev/null || grep -m2 "PROTOBUF_VERSION" /usr/local/include/tf/tensorflow/core/protobuf/*.h 2>/dev/null | head -2
grep -m1 -r "PROTOBUF_VERSION " /usr/local/include/google/protobuf/port_def.inc 2>/dev/null | head -1
echo ""
echo "=== 4. arena_string.h 是否有 SetAllocatedNoArena ==="
grep -c "SetAllocatedNoArena" /usr/local/include/google/protobuf/arena_string.h 2>/dev/null
find /usr/local/include -name "arena_string.h" 2>/dev/null | head -3
echo ""
echo "=== 5. 旧 config.pb.h 生成时间 ==="
ls -la /root/SOC/ly_analyser_src/common/pb_backup/config.pb.h.* 2>/dev/null | head -3
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()