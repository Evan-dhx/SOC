import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("lyprobe 加密相关选项", r"""
echo "=== 1. 帮助中 -3/-4/-5/-6/-c/-r/-E 说明 ==="
tsensor --help 2>&1 | grep -A2 -E "^\s*\[-3|^\s*\[-4|^\s*\[-5|^\s*\[-6|^\s*\[-c\]|^\s*\[-r\]|^\s*\[-E|encrypt|TLS|SSL|tls" | head -30
echo ""
echo "=== 2. 二进制中加密相关字符串 ==="
strings /usr/local/bin/tsensor 2>/dev/null | grep -iE "ssl|tls|encrypt|aes|collector.*sock| -Z" | head -10
echo ""
echo "=== 3. liblyprobe 加密相关 ==="
strings /usr/local/lib/liblyprobe-1.0.0.so 2>/dev/null | grep -iE "tls|ssl|encrypt" | head -10
echo ""
echo "=== 4. 完整帮助（-n 之后部分，看是否提到加密传输） ==="
tsensor --help 2>&1 | sed -n '30,70p'
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()