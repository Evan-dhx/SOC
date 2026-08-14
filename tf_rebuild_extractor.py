import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Update Makefile and rebuild extractor", r"""
echo "=== 1. 修改 Makefile ==="
cd /root/SOC/ly_analyser_src/agent/handlers
cp Makefile Makefile.bak_oldabi

# CXXFLAGS: c++1y -> c++17 + fpermissive
sed -i 's/-std=c++1y/-std=c++17 -fpermissive/' Makefile

# INCS: 更新为新 TF 2.12 头文件路径
sed -i 's#-I/usr/local/include/tf/ -I/usr/local/include/tf/bazel-genfiles -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/tensorflow/third-party -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto#-I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/third_party/eigen3 -I/usr/local/include/tf/tensorflow/core/protobuf -I/usr/local/include/tf/nsync_public#' Makefile

# 去掉 -lprotobuf（用 libtensorflow_cc 内置 + 系统 3.21.9）
sed -i 's/-Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive //' Makefile

# protoc 改为 bazel 3.21.9 版本（系统 protoc 已损坏）
sed -i 's#^\tprotoc \$^ --cpp_out=.#\t/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc $^ --cpp_out=.#' Makefile

echo "--- 修改后关键行 ---"
grep -E "CXXFLAGS=|INCS=|LDLIBS|protoc" Makefile | head -5
echo ""
echo "=== 2. 重编 extractor ==="
rm -f extractor.o extractor
make extractor 2>&1 | tail -15
echo ""
echo "Exit: $?"
ls -lh extractor 2>/dev/null && echo "OK: extractor built" || echo "FAIL"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
