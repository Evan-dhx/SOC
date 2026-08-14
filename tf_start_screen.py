import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("使用 screen 启动 TensorFlow 2.12 编译")
print("=" * 60)

# 安装 screen
print("\n[安装 screen]")
cmd = r"""
yum install -y screen 2>&1 | tail -3
which screen && echo "✓ screen 已安装"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# 清理旧的 screen 会话
print("\n[清理旧会话]")
cmd2 = r"""
screen -S tf_build -X quit 2>/dev/null
sleep 1
echo "✓ 已清理"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 在 screen 中启动编译
print("\n[在 screen 会话中启动编译]")
cmd3 = r"""
# 创建编译脚本
cat > /root/run_tf_build.sh << 'EOF'
#!/bin/bash
cd /root/tensorflow
echo "========================================"
echo "TensorFlow 2.12 编译开始"
echo "时间: $(date)"
echo "========================================"

bazel build \
    --config=opt \
    --local_ram_resources=8192 \
    --jobs=2 \
    //tensorflow:libtensorflow_cc.so \
    //tensorflow:libtensorflow_framework.so

EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 编译成功！"
else
    echo "✗ 编译失败，退出码: $EXIT_CODE"
fi
echo "时间: $(date)"
echo "========================================"
EOF

chmod +x /root/run_tf_build.sh

# 在 screen 会话中启动
screen -dmS tf_build /root/run_tf_build.sh
echo "✓ screen 会话 'tf_build' 已启动"
sleep 2

# 验证 screen 会话
screen -ls
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err.strip() and 'warning' not in err.lower():
    print(f"STDERR: {err}")

# 等待几秒检查进度
time.sleep(5)

print("\n[检查编译状态]")
cmd4 = r"""
echo "=== screen 会话 ==="
screen -ls

echo ""
echo "=== 编译进程 ==="
ps aux | grep -E "bazel|run_tf_build" | grep -v grep | head -5

echo ""
echo "=== bazel 输出 ==="
ls -la /root/.cache/bazel/ 2>/dev/null | head -5
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("✓ TensorFlow 2.12 编译已在 screen 会话中启动")
print("=" * 60)
print("\n管理编译:")
print("  查看实时日志:  screen -r tf_build")
print("  分离会话:      Ctrl+A+D")
print("  检查进度:      python tf_build_monitor.py")
print("  编译完成后:    python tf_upgrade_phase3.py")
