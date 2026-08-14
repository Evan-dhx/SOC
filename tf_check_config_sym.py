import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check Config symbol in libcommon", r"""
echo "=== 1. libcommon.so 中的 Config 符号 ==="
nm -D /lib64/libcommon.so | grep "6config6Config" | head -20
echo ""
echo "=== 2. extractor 需要的 libcommon 符号 ==="
ldd -r /Agent/bin/extractor 2>&1 | grep "undefined" | head -20
echo ""
echo "=== 3. extractor 的 NEEDED ==="
readelf -d /Agent/bin/extractor | grep NEEDED
echo ""
echo "=== 4. 各 libcommon 版本对比 ==="
stat -c "%y %n" /lib64/libcommon.so /usr/lib64/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.so
md5sum /lib64/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.so
echo ""
echo "=== 5. 旧 libcommon 备份 ==="
ls -la /lib64/libcommon* /root/SOC/ly_analyser_src/common/libcommon* 2>/dev/null
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
