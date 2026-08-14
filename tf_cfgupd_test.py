import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_updater 直接测试", r"""
echo "=== 1. 手动 POST 正确配置到 config_updater ==="
cat > /tmp/test_cfg.txt <<'EOF'
controller {
  host: "127.0.0.1"
  port: "10081"
}
dev {
  id: 1
  name: "默认设备"
  type: "netflow"
  agentid: 1
  ip: "127.0.0.1"
  port: 9995
  disabled: false
  flowtype: "netflow"
  pcap_level: 0
  temp: ""
  filter: ""
  interface: "ens192"
  psk: "43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa"
}
EOF
curl -s -X POST "http://127.0.0.1:10081/config_updater" --data-binary @/tmp/test_cfg.txt --max-time 10
echo ""
echo "=== 2. 写入结果 ==="
grep -A11 "^dev {" /Agent/data/config | head -15
echo ""
echo "=== 3. apache CGI 错误日志 ==="
tail -5 /var/log/httpd/error_log 2>/dev/null | grep -i "config\|updater" | head -5
echo ""
echo "=== 4. config_updater 二进制确认 ==="
ls -la /home/Agent/cmd/config_updater
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()