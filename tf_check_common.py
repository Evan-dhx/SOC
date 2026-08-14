import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check common directory build setup", r"""
echo "=== common Makefile ==="
cat /root/SOC/ly_analyser_src/common/Makefile 2>/dev/null | head -50
"""),

    ("Check existing common libs", r"""
echo "=== Existing common libs ==="
ls -lh /root/SOC/ly_analyser_src/common/*.a /root/SOC/ly_analyser_src/common/*.so 2>/dev/null
echo ""
echo "=== Installed libcommon ==="
ls -lh /usr/local/lib/libcommon* /usr/lib64/libcommon* /lib64/libcommon* 2>/dev/null
echo ""
ldconfig -p | grep libcommon
"""),

    ("Check where old libcommon is", r"""
echo "=== Find libcommon ==="
find /root/SOC/ly_analyser_src -name "libcommon*" -type f 2>/dev/null
find /usr/local/lib /usr/lib64 /lib64 -name "libcommon*" 2>/dev/null
"""),

    ("Check common .pb.o files", r"""
echo "=== common directory .o files ==="
ls /root/SOC/ly_analyser_src/common/*.o 2>/dev/null | head -10
echo ""
echo "=== Check if event.pb.cc was recompiled ==="
ls -la /root/SOC/ly_analyser_src/common/event.pb.cc /root/SOC/ly_analyser_src/common/event.pb.o 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
