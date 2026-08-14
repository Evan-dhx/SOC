import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

client.exec_command('mkdir -p /root/SOC/ly_analyser_src/nftls')[1].read()
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\nftls\nftls.c', '/root/SOC/ly_analyser_src/nftls/nftls.c')
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\nftls\Makefile', '/root/SOC/ly_analyser_src/nftls/Makefile')
sftp.close()
print("nftls 源码已同步")

cmds = [
    ("编译 nftls + agent Makefile 规则查看", r"""
echo "=== 1. nftls 编译 ==="
cd /root/SOC/ly_analyser_src/nftls && make 2>&1 | tail -3
ls -la nftls 2>/dev/null
echo ""
echo "=== 2. agent Makefile 编译规则（actl/fsd） ==="
grep -B2 -A6 "actl\|fsd" /root/SOC/ly_analyser_src/agent/handlers/Makefile 2>/dev/null | head -40
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()