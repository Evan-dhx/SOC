import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Build protobuf 3.21.9 from source", r"""
echo "=== Build protobuf 3.21.9 ==="
cd /root/tensorflow/bazel-tensorflow/external/com_google_protobuf
ls -la | head -5
echo ""
echo "--- 检查已有构建产物 ---"
ls -la cmake/build/lib*.so* 2>/dev/null || echo "no cmake build yet"
echo ""
echo "--- 检查版本 ---"
grep "GOOGLE_PROTOBUF_VERSION " src/google/protobuf/stubs/common.h 2>/dev/null || grep -r "3021009" CMakeLists.txt 2>/dev/null | head -2
echo ""
echo "--- 用 cmake 构建（只 libprotobuf，不构建测试） ---"
mkdir -p /tmp/protobuf_build
cd /tmp/protobuf_build
cmake /root/tensorflow/bazel-tensorflow/external/com_google_protobuf \
  -Dprotobuf_BUILD_TESTS=OFF \
  -Dprotobuf_BUILD_SHARED_LIBS=ON \
  -Dprotobuf_BUILD_PROTOC_BINARIES=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  > /tmp/protobuf_cmake.log 2>&1
echo "CMake exit: $?"
tail -5 /tmp/protobuf_cmake.log
echo ""
make -j4 > /tmp/protobuf_make.log 2>&1
echo "Make exit: $?"
tail -10 /tmp/protobuf_make.log
echo ""
ls -lh libprotobuf.so* 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()
