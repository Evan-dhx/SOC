"""
评估 processPlugin 能否修复
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("评估 processPlugin 修复可行性")
print("=" * 60)

cmds = [
    ("processPlugin.c 源码结构", """
cd /root/ly_probe/plugins
echo "=== 文件行数 ==="
wc -l processPlugin.c

echo ""
echo "=== 头文件包含 ==="
head -30 processPlugin.c | grep include

echo ""
echo "=== getProcess 引用 ==="
grep -n 'getProcess' processPlugin.c
"""),
    ("getProcess 函数定义搜索", """
cd /root/ly_probe
echo "=== 在所有源码中搜索 getProcess ==="
grep -rn 'getProcess' *.c *.h plugins/*.c plugins/*.h 2>/dev/null
"""),
    ("processPlugin 完整依赖分析", """
cd /root/ly_probe/plugins
echo "=== 未解析的外部符号 ==="
gcc -shared -fPIC -O2 -DHAVE_CONFIG_H -I.. -I/usr/local/include \
    -o /tmp/test_processPlugin.so processPlugin.c 2>&1 | head -20

echo ""
echo "=== nm 检查未定义符号 ==="
nm -u /usr/local/lib/lyprobe/plugins/processPlugin.so 2>/dev/null | head -20
"""),
    ("processPlugin 功能描述", """
cd /root/ly_probe/plugins
echo "=== 插件描述 ==="
grep -A5 'PluginInfo.*processPlugin\\|processPluginEntryFctn\\|PluginEntryFctn' processPlugin.c | head -20

echo ""
echo "=== 主要函数 ==="
grep -n '^[a-zA-Z].*(' processPlugin.c | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n{'='*50}")
    print(f"=== {label} ===")
    print(f"{'='*50}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()
