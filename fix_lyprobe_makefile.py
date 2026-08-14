"""
安装 lyprobe
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("安装 lyprobe")
print("=" * 60)

install_cmd = """
cd /root/ly_probe

echo "=== 安装 lyprobe ==="
make install 2>&1 | tail -20

echo ""
echo "=== 验证安装 ==="
which lyprobe
ls -la /usr/local/bin/lyprobe 2>/dev/null || echo "not found in /usr/local/bin"

echo ""
echo "=== 测试 lyprobe ==="
lyprobe --help 2>&1 | head -15 || /usr/local/bin/lyprobe --help 2>&1 | head -15

echo ""
echo "=== 复制规则文件 ==="
# 复制指纹规则到正确位置
if [ -d /root/ly_probe/fp-patterns ]; then
    mkdir -p /usr/local/lib/lyprobe/plugins
    cp -r /root/ly_probe/fp-patterns /usr/local/lib/lyprobe/plugins/
    echo "已复制 fp-patterns 规则"
fi

if [ -d /root/ly_probe/l7-patterns ]; then
    cp -r /root/ly_probe/l7-patterns /usr/local/lib/lyprobe/plugins/
    echo "已复制 l7-patterns 规则"
fi

echo ""
echo "=== 最终验证 ==="
ls -la /usr/local/bin/lyprobe
ls -la /usr/local/lib/lyprobe/plugins/ 2>/dev/null || echo "plugins dir not found"
"""

stdin, stdout, stderr = client.exec_command(install_cmd, timeout=120)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("lyprobe 安装完成!")
print("=" * 60)
print("\n使用示例:")
print("  lyprobe -i eth0 -n 127.0.0.1:9995 -e 0 -w 32768 -G")
