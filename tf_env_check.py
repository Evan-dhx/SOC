import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("环境检查", r"""
echo "=== 1. Python 与 pip ==="
python3 --version
python3 -m pip --version 2>&1 | head -1
echo ""
echo "=== 2. pymysql 可用性 ==="
python3 -c "import pymysql; print('pymysql', pymysql.__version__)" 2>&1
echo ""
echo "=== 3. openssl ==="
openssl version 2>&1
echo ""
echo "=== 4. MySQL 与 root 访问 ==="
mysql --version 2>&1
mysql -uroot -ppassword123 -e "SELECT VERSION(); SHOW DATABASES;" 2>&1 | head -12
echo ""
echo "=== 5. 防火墙/端口占用 ==="
ss -tlnp 2>/dev/null | grep -E "8090|8091" || echo "8090/8091 空闲"
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