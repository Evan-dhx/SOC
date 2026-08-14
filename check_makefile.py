"""
检查并修复 nprobe.h 中的头文件包含条件
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("检查 nprobe.h 头文件包含")
print("=" * 60)

# 查看 nprobe.h 中 ether 相关头文件的上下文
check_cmd = """
cd /root/ly_probe

echo "=== 查看 nprobe.h 中 ether 相关头文件上下文 ==="
grep -B5 -A2 "ether" nprobe.h | head -40

echo ""
echo "=== 查看 config.h 中的相关定义 ==="
grep -i "ether\|HAVE_NET" config.h 2>/dev/null || echo "config.h 中无相关定义"

echo ""
echo "=== 测试编译一个简单程序 ==="
cat > /tmp/test_ether.c << 'EOF'
#include <stdio.h>
#include <net/ethernet.h>
int main() {
    struct ether_header eh;
    printf("ether_header size: %zu\\n", sizeof(eh));
    return 0;
}
EOF
gcc /tmp/test_ether.c -o /tmp/test_ether 2>&1 && echo "编译成功" || echo "编译失败"
/tmp/test_ether 2>/dev/null
"""

stdin, stdout, stderr = client.exec_command(check_cmd, timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
