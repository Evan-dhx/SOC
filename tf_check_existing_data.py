import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("现有表数据 + 密码猜测验证", r"""
echo "=== 1. 现有 t_mogroup ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_mogroup;" 2>&1
echo ""
echo "=== 2. 现有 t_device/t_agent/t_config ==="
mysql -uroot -ppassword123 server -e "SELECT * FROM t_device; SELECT * FROM t_agent; SELECT * FROM t_config;" 2>&1
echo ""
echo "=== 3. 官方密码 MD5 验证 ==="
for p in admin Abyss@123 123456 abyss123 Abyss@2023 liuying LiuYing@123 abyssal abyss; do
  H=$(echo -n "$p" | md5sum | cut -d' ' -f1)
  if [ "$H" == "0b2c6435092cd5e4bafe47fdf1e92e9c" ]; then
    echo "找到密码: $p"
  fi
done
echo "验证完成"
echo ""
echo "=== 4. config_event.cpp 所在 lib 目录编译状态 ==="
ls -la /root/SOC/ly_server_src/lib/config_event.cpp 2>/dev/null | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 5. config CGI 调用的函数（config.cpp 全文关键行） ==="
grep -n "config_event\|op_\|action\|type\|ConfigEvent" /root/SOC/ly_server_src/server/config.cpp | head -15
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
