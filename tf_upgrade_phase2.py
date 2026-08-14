import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("TensorFlow 2.12 升级 - 阶段 2: 安装依赖与启动编译")
print("=" * 60)

cmds = [
    ("添加 swap 空间", r"""
# 添加 8GB swap 文件（编译 TF 需要大量内存）
if [ ! -f /swapfile_tf ]; then
    echo "创建 8GB swap 文件..."
    dd if=/dev/zero of=/swapfile_tf bs=1G count=8 status=progress
    chmod 600 /swapfile_tf
    mkswap /swapfile_tf
    swapon /swapfile_tf
    echo "/swapfile_tf none swap sw 0 0" >> /etc/fstab
    echo "Swap 已添加"
else
    echo "Swap 文件已存在"
fi
free -h | grep Swap
"""),
    
    ("安装 Bazel 5.3.0", r"""
# 安装 Bazel（TF 2.12 需要 Bazel 5.3.0）
if ! command -v bazel &> /dev/null; then
    echo "安装 Bazel 5.3.0..."
    cd /tmp
    curl -L -o bazel-5.3.0-installer-linux-x86_64.sh https://github.com/bazelbuild/bazel/releases/download/5.3.0/bazel-5.3.0-installer-linux-x86_64.sh
    chmod +x bazel-5.3.0-installer-linux-x86_64.sh
    ./bazel-5.3.0-installer-linux-x86_64.sh
    echo "Bazel 安装完成"
else
    echo "Bazel 已安装"
fi
bazel --version
"""),
    
    ("下载 TensorFlow 2.12 源码", r"""
# 下载 TF 2.12 源码
cd /root
if [ ! -d /root/tensorflow ]; then
    echo "下载 TensorFlow 2.12..."
    git clone --depth 1 --branch v2.12.0 https://github.com/tensorflow/tensorflow.git
    echo "下载完成"
else
    echo "TensorFlow 源码已存在"
fi
ls -ld /root/tensorflow
"""),
    
    ("配置 TensorFlow 编译", r"""
cd /root/tensorflow

# 创建 TF 编译配置文件
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

echo "TF 编译配置完成"
cat .tf_configure.bazelrc
"""),
    
    ("启动 TensorFlow 编译（后台）", r"""
cd /root/tensorflow

# 检查是否已经在编译
if pgrep -f "bazel build" > /dev/null; then
    echo "编译已在进行中"
    ps aux | grep "bazel build" | grep -v grep
else
    echo "启动 TensorFlow 2.12 编译..."
    echo "这可能需要 4-8 小时，日志保存在 /tmp/tf_build.log"
    
    # 使用 nohup 在后台编译，限制资源使用
    nohup bazel build \
        --config=opt \
        --local_ram_resources=8192 \
        --jobs=2 \
        //tensorflow:libtensorflow_cc.so \
        //tensorflow:libtensorflow_framework.so \
        > /tmp/tf_build.log 2>&1 &
    
    echo "编译进程 PID: $!"
    sleep 2
    
    # 验证进程已启动
    if pgrep -f "bazel build" > /dev/null; then
        echo "✓ 编译已成功启动"
    else
        echo "✗ 编译启动失败，检查日志："
        tail -20 /tmp/tf_build.log
    fi
fi
"""),
    
    ("查看编译进度", r"""
echo "=== 编译进程状态 ==="
ps aux | grep "bazel" | grep -v grep | head -5

echo ""
echo "=== 最新编译日志 ==="
if [ -f /tmp/tf_build.log ]; then
    tail -30 /tmp/tf_build.log
else
    echo "日志文件尚未创建"
fi
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print(f"STDERR: {err}")

client.close()

print("\n" + "=" * 60)
print("阶段 2 完成：编译已启动")
print("=" * 60)
print("\n监控编译进度：")
print("  tail -f /tmp/tf_build.log")
print("\n检查编译是否完成：")
print("  ps aux | grep 'bazel build'")
print("  # 如果没有输出，说明编译已完成")
print("\n编译完成后，运行 tf_upgrade_phase3.py 安装库文件并重新编译分析引擎")
