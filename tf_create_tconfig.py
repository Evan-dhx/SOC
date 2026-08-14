import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Create t_config and rerun", r"""
echo "=== 1. 创建 t_config 表 ==="
mysql -e "CREATE TABLE IF NOT EXISTS server.t_config (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(64), value VARCHAR(255));" 2>&1
mysql -e "INSERT INTO server.t_config (name, value) VALUES ('controller_host','127.0.0.1'),('controller_port','10081') ON DUPLICATE KEY UPDATE value=VALUES(value);" 2>&1
mysql -e "SELECT * FROM server.t_config;" 2>/dev/null
echo ""
echo "=== 2. 运行 config_pusher debug ==="
cd /Server/bin
./config_pusher d 2>&1 | head -40
echo "EXIT:$?"
echo ""
echo "=== 3. config 文件 ==="
ls -la /Agent/data/config
echo "大小: $(stat -c%s /Agent/data/config 2>/dev/null) 字节"
echo ""
echo "=== 4. config 内容（文本） ==="
strings /Agent/data/config 2>/dev/null | head -15
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
