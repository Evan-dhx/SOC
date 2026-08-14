import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("threatconf 500 诊断", r"""
echo "=== 1. 最新错误日志 ==="
tail -8 /var/log/httpd/ly_error_log 2>/dev/null | grep -v "AH00489\|AH00094\|AH02282\|AH01232\|AH00492\|suexec\|mpm_event" | tail -6
echo ""
echo "=== 2. 符号检查 ==="
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r /Server/www/d/threatconf 2>&1 | grep -c "undefined"
echo ""
echo "=== 3. 直接运行测试 ==="
echo 'op: get' | timeout 20 /Server/www/d/threatconf 2>&1 | head -c 200
echo "退出码: $?"
echo ""
echo "=== 4. 文件属主 ==="
ls -la /Server/www/d/threatconf
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()