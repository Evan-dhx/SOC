import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("TensorFlow 2.12 升级 - 阶段 1: 环境检查与编译启动")
print("=" * 60)

# Phase 1: Environment check
cmds = [
    ("检查系统资源", r"""
echo "=== 系统信息 ==="
cat /etc/os-release | grep PRETTY_NAME
echo ""
echo "=== GCC 版本 ==="
gcc --version | head -1
echo ""
echo "=== 内存 ==="
free -h | head -2
echo ""
echo "=== 磁盘空间 ==="
df -h / | tail -1
echo ""
echo "=== CPU 核心数 ==="
nproc
"""),
    
    ("检查当前 TensorFlow", r"""
echo "=== 当前 TF 库 ==="
ls -lh /usr/local/lib/libtensorflow* 2>/dev/null
echo ""
echo "=== 当前 TF 头文件 ==="
ls -d /usr/local/include/tf 2>/dev/null && echo "存在" || echo "不存在"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("阶段 1 完成：环境检查")
print("=" * 60)
print("\n下一步操作：")
print("1. 确保服务器有至少 16GB 内存和 20GB 磁盘空间")
print("2. 运行 tf_upgrade_phase2.py 安装 Bazel 并启动 TensorFlow 2.12 编译")
print("   注意：编译过程需要 2-4 小时，建议使用 screen 或 tmux")
print("\n命令示例：")
print("  screen -S tf_build")
print("  python tf_upgrade_phase2.py")
print("  # 按 Ctrl+A+D 分离会话，稍后用 screen -r tf_build 重新连接")
