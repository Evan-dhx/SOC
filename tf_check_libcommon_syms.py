import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("检查 libcommon.so 符号", r"""
echo "=== 1. libcommon.so 是否导出 FeatureResponse 构造 ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep -E "FeatureResponseC|FeatureRecordC|GenEventResC" | head -10
echo ""
echo "=== 2. libcommon.a 静态库是否包含 ==="
nm /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null | grep -E "FeatureResponseC1|FeatureRecordC1" | head -6
echo ""
echo "=== 3. feature.pb.cc 中构造函数定义方式 ==="
grep -n "FeatureResponse::FeatureResponse\|FeatureRecord::FeatureRecord" /root/SOC/ly_analyser_src/common/feature.pb.cc 2>/dev/null | head -6
echo ""
echo "=== 4. flow 目录 Makefile ==="
cat /root/SOC/ly_analyser_src/agent/flow/Makefile 2>/dev/null | head -40
echo ""
echo "=== 5. flow_filter_noai.a 内容 ==="
ar t /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
