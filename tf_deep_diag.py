import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Deep diagnostics", r"""
echo "=== 1. ldd -r 完整重定位检查 ==="
cd /Agent/bin
ldd -r ./extractor 2>&1 | grep -E "undefined|not found" | head -10
echo ""
echo "=== 2. libcommon.so 符号需求 ==="
nm -D /lib64/libcommon.so | grep "CopyWithSourceCheck"
echo ""
echo "=== 3. libprotobuf.so.19 的 SONAME ==="
readelf -d /usr/local/lib/libprotobuf.so.19 | grep SONAME
echo ""
echo "=== 4. extractor 的 RPATH ==="
readelf -d /Agent/bin/extractor | grep -E "RPATH|RUNPATH"
echo ""
echo "=== 5. LD_LIBRARY_PATH ==="
env | grep LD_
echo ""
echo "=== 6. 最小测试程序 ==="
cat > /tmp/test_proto.cpp << 'EOF'
#include <google/protobuf/message.h>
#include <cstdio>
int main() {
    printf("protobuf loaded OK, MessageLite size=%zu\n", sizeof(google::protobuf::MessageLite));
    return 0;
}
EOF
g++ -o /tmp/test_proto /tmp/test_proto.cpp -I/usr/local/include -L/usr/local/lib -lprotobuf
/tmp/test_proto && echo "direct link OK"
echo ""
echo "=== 7. 直接 dlopen libcommon 测试 ==="
cat > /tmp/test_common.cpp << 'EOF'
#include <dlfcn.h>
#include <cstdio>
int main() {
    void* h = dlopen("/lib64/libcommon.so", RTLD_NOW | RTLD_GLOBAL);
    if (!h) { printf("dlopen failed: %s\n", dlerror()); return 1; }
    printf("libcommon loaded OK\n");
    return 0;
}
EOF
g++ -o /tmp/test_common /tmp/test_common.cpp -ldl
LD_LIBRARY_PATH=/usr/local/lib /tmp/test_common
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
