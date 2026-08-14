import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("安装 pymysql + 建库", r"""
echo "=== 1. OS 版本 ==="
cat /etc/os-release | head -3
echo ""
echo "=== 2. 尝试安装 pymysql ==="
python3 -c "import pymysql; print('已存在')" 2>/dev/null || yum install -y python3-PyMySQL 2>&1 | tail -3
echo ""
echo "=== 3. 验证 ==="
python3 -c "import pymysql; print('pymysql', pymysql.__version__)" 2>&1
echo ""
echo "=== 4. 创建 ti_server 数据库 ==="
mysql -uroot -ppassword123 -e "CREATE DATABASE IF NOT EXISTS ti_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; SHOW DATABASES;" 2>&1 | grep -E "ti_server|Database"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()