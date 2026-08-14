import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("修复依赖问题并重新启动 TF 2.12 编译")
print("=" * 60)

cmds = [
    ("安装缺失依赖", r"""
echo "=== 安装 git, unzip 等依赖 ==="
yum install -y git unzip zip patch which 2>&1 | tail -5
echo ""
echo "验证:"
which git && echo "✓ git"
which unzip && echo "✓ unzip"
"""),

    ("重新安装 Bazel 5.3.0", r"""
echo "=== 重新安装 Bazel ==="
cd /tmp
if ! command -v bazel &> /dev/null; then
    ./bazel-5.3.0-installer-linux-x86_64.sh 2>&1 | tail -5
    echo "Bazel 安装完成"
fi
bazel --version
"""),

    ("克隆 TensorFlow 2.12 源码", r"""
echo "=== 克隆 TensorFlow 2.12 ==="
cd /root
if [ ! -d /root/tensorflow ]; then
    git clone --depth 1 --branch v2.12.0 https://github.com/tensorflow/tensorflow.git 2>&1 | tail -5
    echo "克隆完成"
else
    echo "TensorFlow 源码已存在"
fi
ls -ld /root/tensorflow
du -sh /root/tensorflow
"""),

    ("配置 TF 编译", r"""
cd /root/tensorflow

# 创建编译配置
cat > .tf_configure.bazelrc << 'EOF'
build --action_env PYTHON_BIN_PATH=/usr/bin/python3
build --action_env PYTHON_LIB_PATH=/usr/lib64/python3.9/site-packages
build --python_path=/usr/bin/python3
build --action_env TF_CONFIGURE_IOS=0
build --action_env TF_NEED_ROCM=0
build --action_env TF_NEED_CUDA=0
build --action_env TF_NEED_TENSORRT=0
build --action_env TF_NEED_OPENCL_SYCL=0
build --action_env TF_NEED_OPENCL=0
build --action_env TF_SET_ANDROID_WORKSPACE=0
build --action_env TF_DOWNLOAD_CLANG=0
build --action_env TF_NEED_MPI=0
build --action_env CC_OPT_FLAGS="-march=native"
EOF

echo "✓ 配置完成"
"""),

    ("启动后台编译", r"""
cd /root/tensorflow

# 确认没有在编译
pkill -f "bazel build" 2>/dev/null
sleep 1

echo "启动 TensorFlow 2.12 编译..."
echo "日志: /tmp/tf_build.log"

nohup bazel build \
    --config=opt \
    --local_ram_resources=8192 \
    --jobs=2 \
    //tensorflow:libtensorflow_cc.so \
    //tensorflow:libtensorflow_framework.so \
    > /tmp/tf_build.log 2>&1 &

BUILD_PID=$!
echo "编译进程 PID: $BUILD_PID"
sleep 3

# 验证进程
if kill -0 $BUILD_PID 2>/dev/null; then
    echo "✓ 编译已成功启动"
else
    echo "✗ 编译启动失败"
    echo "=== 日志 ==="
    cat /tmp/tf_build.log
fi
"""),

    ("查看初始日志", r"""
echo "=== 编译初始日志 ==="
sleep 5
if [ -f /tmp/tf_build.log ]; then
    tail -20 /tmp/tf_build.log
else
    echo "日志文件尚未创建"
fi

echo ""
echo "=== 进程状态 ==="
ps aux | grep bazel | grep -v grep | head -3
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print(f"STDERR: {err}")

client.close()

print("\n" + "=" * 60)
print("编译已启动！")
print("=" * 60)
print("\n监控进度: python tf_build_monitor.py")
print("编译完成后: python tf_upgrade_phase3.py")
