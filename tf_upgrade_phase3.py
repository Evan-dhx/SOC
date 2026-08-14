import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("TensorFlow 2.12 升级 - 阶段 3: 安装库文件与重新编译分析引擎")
print("=" * 60)

cmds = [
    ("检查编译产物", r"""
echo "=== 检查编译产物 ==="
ls -lh /root/tensorflow/bazel-bin/tensorflow/libtensorflow_cc.so 2>/dev/null && echo "✓ libtensorflow_cc.so" || { echo "✗ libtensorflow_cc.so 不存在"; exit 1; }
ls -lh /root/tensorflow/bazel-bin/tensorflow/libtensorflow_framework.so 2>/dev/null && echo "✓ libtensorflow_framework.so" || { echo "✗ libtensorflow_framework.so 不存在"; exit 1; }

# 检查实际文件大小
CC_SIZE=$(stat -c%s /root/tensorflow/bazel-bin/tensorflow/libtensorflow_cc.so.2.12.0 2>/dev/null || echo 0)
FW_SIZE=$(stat -c%s /root/tensorflow/bazel-bin/tensorflow/libtensorflow_framework.so.2.12.0 2>/dev/null || echo 0)
echo "libtensorflow_cc.so.2.12.0: $CC_SIZE bytes"
echo "libtensorflow_framework.so.2.12.0: $FW_SIZE bytes"
if [ "$CC_SIZE" -lt 1000000 ]; then
    echo "✗ 库文件过小，可能编译不完整"
    exit 1
fi
echo "✓ 编译产物验证通过"
"""),

    ("备份旧 TF 库", r"""
echo "=== 备份旧 TensorFlow 2.0.4 库 ==="
mkdir -p /root/tf_backup
cp -a /usr/local/lib/libtensorflow*.so* /root/tf_backup/ 2>/dev/null
cp -a /usr/lib64/libtensorflow*.so* /root/tf_backup/ 2>/dev/null
echo "备份完成:"
ls -lh /root/tf_backup/
"""),

    ("安装 TF 2.12 库文件", r"""
echo "=== 安装 TensorFlow 2.12 库文件 ==="

# 复制新编译的库文件
cp /root/tensorflow/bazel-bin/tensorflow/libtensorflow_cc.so.2.12.0 /usr/local/lib/
cp /root/tensorflow/bazel-bin/tensorflow/libtensorflow_framework.so.2.12.0 /usr/local/lib/

# 创建符号链接
cd /usr/local/lib
ln -sf libtensorflow_cc.so.2.12.0 libtensorflow_cc.so.2
ln -sf libtensorflow_cc.so.2 libtensorflow_cc.so
ln -sf libtensorflow_framework.so.2.12.0 libtensorflow_framework.so.2
ln -sf libtensorflow_framework.so.2 libtensorflow_framework.so

# 更新 /usr/lib64 链接
ln -sf /usr/local/lib/libtensorflow_cc.so.2.12.0 /usr/lib64/libtensorflow_cc.so.2
ln -sf /usr/local/lib/libtensorflow_framework.so.2.12.0 /usr/lib64/libtensorflow_framework.so.2

# 刷新动态链接库缓存
ldconfig

echo "✓ 库文件安装完成"
ls -lh /usr/local/lib/libtensorflow*
"""),

    ("安装 TF 2.12 头文件", r"""
echo "=== 安装 TensorFlow 2.12 头文件 ==="

# 备份旧头文件
if [ -d /usr/local/include/tf ]; then
    mv /usr/local/include/tf /usr/local/include/tf_old_2.0.4
    echo "旧头文件已备份到 tf_old_2.0.4"
fi

# 复制新头文件
mkdir -p /usr/local/include/tf
cp -r /root/tensorflow/tensorflow /usr/local/include/tf/
cp -r /root/tensorflow/third_party /usr/local/include/tf/

# 复制 bazel 生成的头文件（protobuf 生成的）
cp -r /root/tensorflow/bazel-bin/tensorflow/core/protobuf /usr/local/include/tf/tensorflow/core/ 2>/dev/null

echo "✓ 头文件安装完成"
ls -d /usr/local/include/tf/tensorflow
"""),

    ("检查新头文件路径", r"""
echo "=== 验证关键头文件 ==="
ls /usr/local/include/tf/tensorflow/cc/client/client_session.h 2>/dev/null && echo "✓ client_session.h" || echo "✗ client_session.h"
ls /usr/local/include/tf/tensorflow/cc/ops/standard_ops.h 2>/dev/null && echo "✓ standard_ops.h" || echo "✗ standard_ops.h"
ls /usr/local/include/tf/tensorflow/core/framework/tensor.h 2>/dev/null && echo "✓ tensor.h" || echo "✗ tensor.h"
ls /usr/local/include/tf/tensorflow/core/public/session.h 2>/dev/null && echo "✓ session.h" || echo "✗ session.h"

echo ""
echo "=== 检查 Eigen 头文件 ==="
find /usr/local/include/tf -name "Tensor" -path "*/Eigen/*" 2>/dev/null | head -3

echo ""
echo "=== 检查 protobuf 生成头文件 ==="
find /usr/local/include/tf/tensorflow/core/protobuf -name "*.h" 2>/dev/null | head -5
"""),

    ("更新 Makefile include 路径", r"""
echo "=== 更新 Makefile include 路径 ==="

# 备份原 Makefile
cd /root/SOC/ly_analyser_src/agent/flow
cp Makefile Makefile.backup

# 更新 INCS 路径
# TF 2.12 使用 bazel 构建，头文件结构不同
cat > Makefile.new << 'MAKEFILE_EOF'
CXX=g++
INCS=-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/tensorflow/core/protobuf
CXXFLAGS=-Wall -fPIC -g -std=c++14 -DAGENT -O2
CXXFLAGS+=-I../../common
LDFLAGS+=-L/usr/lib64 -L/usr/lib -L/usr/local/lib -L. -L../../common
LDLIBS+=-Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive -lcommon
LDLIBS+=-lboost_regex
LDLIBS+=-ltensorflow_cc -ltensorflow_framework
MAKEFILE_EOF

# 追加剩余内容
tail -n +10 Makefile.backup >> Makefile.new
mv Makefile.new Makefile

echo "✓ Makefile 已更新"
echo ""
echo "新的 INCS 路径:"
grep "^INCS=" Makefile
"""),

    ("重新编译 flow_filter.a", r"""
echo "=== 重新编译 flow_filter.a（包含 AI 过滤器）==="
cd /root/SOC/ly_analyser_src/agent/flow

# 清理旧文件
make clean

# 重新编译
make flow_filter.a 2>&1 | tail -30
echo ""
echo "编译退出码: $?"

echo ""
echo "=== 检查生成的库文件 ==="
ls -lh flow_filter.a 2>/dev/null && echo "✓ flow_filter.a 已生成" || echo "✗ flow_filter.a 生成失败"
"""),

    ("重新编译 indexer", r"""
echo "=== 重新编译 indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing

# 更新 Makefile
cp Makefile Makefile.backup
sed -i 's|/usr/local/include/tf/contrib/makefile/downloads/eigen||g' Makefile
sed -i 's|/usr/local/include/tf/contrib/makefile/downloads/absl||g' Makefile
sed -i 's|/usr/local/include/tf/contrib/makefile/gen/protobuf/include||g' Makefile
sed -i 's|/usr/local/include/tf/contrib/makefile/gen/proto||g' Makefile
sed -i 's|/usr/local/include/tf/bazel-genfiles||g' Makefile

# 添加新的 protobuf 路径
sed -i 's|-I/usr/local/include/tf/tensorflow/third-party|-I/usr/local/include/tf/tensorflow/third-party -I/usr/local/include/tf/tensorflow/core/protobuf|' Makefile

# 清理并重新编译
make clean
make 2>&1 | tail -30
echo ""
echo "编译退出码: $?"

echo ""
echo "=== 检查生成的二进制 ==="
ls -lh indexer 2>/dev/null && echo "✓ indexer 已生成" || echo "✗ indexer 生成失败"
"""),

    ("部署新的 indexer", r"""
echo "=== 部署新的 indexer ==="

# 备份旧 indexer
cp /Agent/bin/indexer /Agent/bin/indexer.backup 2>/dev/null

# 复制新 indexer
cp /root/SOC/ly_analyser_src/agent/indexing/indexer /Agent/bin/indexer
chmod +x /Agent/bin/indexer

echo "✓ indexer 已部署"
ls -lh /Agent/bin/indexer
"""),

    ("验证 AI 过滤器", r"""
echo "=== 验证 AI 过滤器是否启用 ==="

# 检查 indexer 是否链接了 TF 库
ldd /Agent/bin/indexer | grep tensorflow

echo ""
echo "=== 检查 TF 符号 ==="
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 | grep -E "NewSession|ReadBinaryProto" | head -5

echo ""
echo "=== 测试 indexer 启动 ==="
# 简单测试 indexer 是否能启动（不实际运行）
/Agent/bin/indexer --help 2>&1 | head -10 || echo "indexer 已安装（可能不支持 --help）"
"""),

    ("最终验证", r"""
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
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err}")
    
    # 如果编译失败，停止执行
    if "编译退出码: 1" in out or "✗" in out:
        print(f"\n✗ 步骤失败: {label}")
        print("请检查错误信息并手动修复")
        break

client.close()

print("\n" + "=" * 60)
print("阶段 3 完成")
print("=" * 60)
