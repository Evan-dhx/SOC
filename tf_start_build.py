import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("启动 TensorFlow 2.12 编译")
print("=" * 60)

# 创建启动脚本
print("\n[创建编译启动脚本]")
cmd = r"""
cat > /root/start_tf_build.sh << 'SCRIPT'
#!/bin/bash
cd /root/tensorflow
echo "开始编译 TensorFlow 2.12..." > /tmp/tf_build.log
echo "时间: $(date)" >> /tmp/tf_build.log
echo "" >> /tmp/tf_build.log

bazel build \
    --config=opt \
    --local_ram_resources=8192 \
    --jobs=2 \
    //tensorflow:libtensorflow_cc.so \
    //tensorflow:libtensorflow_framework.so \
    >> /tmp/tf_build.log 2>&1

EXIT_CODE=$?
echo "" >> /tmp/tf_build.log
echo "编译完成，退出码: $EXIT_CODE" >> /tmp/tf_build.log
echo "时间: $(date)" >> /tmp/tf_build.log
SCRIPT

chmod +x /root/start_tf_build.sh
echo "✓ 启动脚本已创建"
cat /root/start_tf_build.sh
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# 使用 nohup 启动
print("\n[启动编译进程]")
cmd2 = r"""
# 先清理旧进程
pkill -f "bazel build" 2>/dev/null
sleep 1

# 使用 nohup 启动
cd /root/tensorflow
nohup /root/start_tf_build.sh > /dev/null 2>&1 &
echo "启动 PID: $!"
sleep 3

# 验证
echo ""
echo "=== 进程检查 ==="
ps aux | grep -E "bazel|start_tf" | grep -v grep

echo ""
echo "=== 日志检查 ==="
if [ -f /tmp/tf_build.log ]; then
    echo "日志文件存在"
    cat /tmp/tf_build.log
else
    echo "日志文件尚未创建"
fi
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print(f"STDERR: {err}")

# 等待几秒再检查
import time
time.sleep(5)

print("\n[5秒后再次检查]")
cmd3 = r"""
echo "=== 进程状态 ==="
ps aux | grep bazel | grep -v grep | head -5

echo ""
echo "=== 最新日志 ==="
if [ -f /tmp/tf_build.log ]; then
    wc -l /tmp/tf_build.log
    tail -30 /tmp/tf_build.log
else
    echo "日志文件不存在"
fi
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
