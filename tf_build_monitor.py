import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("TensorFlow 2.12 编译进度监控")
print("=" * 60)

cmds = [
    ("编译进程状态", r"""
if pgrep -f "bazel" > /dev/null; then
    echo "状态: 编译中..."
    echo ""
    echo "进程列表:"
    ps aux | grep bazel | grep -v grep | head -5
else
    echo "状态: 编译已完成（或尚未启动）"
fi
"""),
    
    ("最新编译日志", r"""
if [ -f /tmp/tf_build.log ]; then
    echo "日志文件大小:"
    ls -lh /tmp/tf_build.log
    echo ""
    echo "最后 50 行:"
    tail -50 /tmp/tf_build.log
else
    echo "日志文件不存在"
fi
"""),
    
    ("系统资源使用", r"""
echo "内存使用:"
free -h | head -2
echo ""
echo "CPU 负载:"
uptime
echo ""
echo "磁盘空间:"
df -h / | tail -1
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("提示:")
print("  - 编译通常需要 4-8 小时")
print("  - 完成后运行: python tf_upgrade_phase3.py")
print("=" * 60)
