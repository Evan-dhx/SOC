import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find all libprotobuf locations", r"""
echo "=== 1. 系统中所有 libprotobuf ==="
find / -name "libprotobuf.so*" -type f -o -name "libprotobuf.so*" -type l 2>/dev/null | grep -v bazel
echo ""
echo "=== 2. ld.so.conf 配置 ==="
cat /etc/ld.so.conf
ls /etc/ld.so.conf.d/
cat /etc/ld.so.conf.d/*.conf 2>/dev/null
"""),

    ("LD_DEBUG trace of extractor", r"""
echo "=== 3. LD_DEBUG 追踪加载 ==="
cd /Agent/bin
LD_DEBUG=libs timeout 5 sudo -u apache ./extractor -v 1 2>&1 | grep -iE "protobuf|common|trying file|cache" | head -30
"""),

    ("Check SONAME of actual file", r"""
echo "=== 4. 实际文件 SONAME ==="
readelf -d /usr/local/lib/libprotobuf.so.19.0.0 | grep -E "SONAME"
echo ""
echo "=== 5. 文件 hash 对比 ==="
md5sum /usr/local/lib/libprotobuf.so.19.0.0 /tmp/protobuf_build/libprotobuf.so.3.21.9.0
echo ""
echo "=== 6. /lib64 检查 ==="
ls -la /lib64/libprotobuf* /usr/lib64/libprotobuf* 2>/dev/null
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
