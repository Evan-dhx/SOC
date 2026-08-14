import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译进程状态", r"""
echo "=== 1. 当前 g++/make 进程 ==="
ps aux | grep -E "g\+\+|make all" | grep -v grep | awk '{print $2, $3, $4, $11, $12, $13, $14}' | head -5
echo ""
echo "=== 2. 日志行数 ==="
wc -l /tmp/rebuild_all.log
echo ""
echo "=== 3. 最后一个编译的文件（.o 时间戳） ==="
ls -la /root/SOC/ly_analyser_src/agent/handlers/*.o 2>/dev/null | sort -k6,8 | tail -5 | awk '{print $NF, $6, $7, $8}'
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()