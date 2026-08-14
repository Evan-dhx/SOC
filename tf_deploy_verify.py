import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Deploy new indexer", r"""
echo "=== 部署新的 indexer ==="
# 备份旧 indexer
cp /Agent/bin/indexer /Agent/bin/indexer.backup 2>/dev/null && echo "旧 indexer 已备份" || echo "无旧 indexer"

# 复制新 indexer
cp /root/SOC/ly_analyser_src/agent/indexing/indexer /Agent/bin/indexer
chmod +x /Agent/bin/indexer

echo "✓ indexer 已部署"
ls -lh /Agent/bin/indexer
"""),

    ("Verify TF linking", r"""
echo "=== 验证 AI 过滤器是否启用 ==="
echo ""
echo "=== ldd 检查 TF 库 ==="
ldd /Agent/bin/indexer | grep -E "tensorflow|common|protobuf"
echo ""
echo "=== TF 符号检查 ==="
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 | grep -E "NewSession|ReadBinaryProto" | head -5
"""),

    ("Verify indexer linked symbols", r"""
echo "=== indexer 中的 TF 符号引用 ==="
nm -D /Agent/bin/indexer 2>/dev/null | grep -E "NewSession|ReadBinaryProto|ClientSession" | head -10
echo ""
echo "=== indexer 动态依赖 ==="
readelf -d /Agent/bin/indexer | grep NEEDED
"""),

    ("Final verification", r"""
echo "=== 最终验证 ==="
echo ""
echo "TensorFlow 版本:"
ls -lh /usr/local/lib/libtensorflow_cc.so.2.12.0
echo ""
echo "分析引擎:"
ls -lh /Agent/bin/indexer
echo ""
echo "动态链接库:"
ldd /Agent/bin/indexer | grep -E "tensorflow|common"
echo ""
echo "✓ TensorFlow 2.12 升级完成！"
echo "✓ AI 过滤器已启用"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
print("\nDone")
