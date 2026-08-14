import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("创建用户表 + 测试登录", r"""
echo "=== 1. 创建表 ==="
mysql -uroot -ppassword123 server 2>&1 <<'EOF'
CREATE TABLE IF NOT EXISTS t_user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  pass VARCHAR(64) NOT NULL,
  level VARCHAR(16) DEFAULT 'VIEWER',
  resource VARCHAR(255) DEFAULT '',
  disabled CHAR(1) DEFAULT 'N',
  lockedtime INT DEFAULT 0,
  lasttime INT DEFAULT 0,
  lastip BIGINT DEFAULT 0,
  lastsession VARCHAR(32) DEFAULT ''
);
CREATE TABLE IF NOT EXISTS t_user_session (
  sid VARCHAR(32) PRIMARY KEY,
  uid INT NOT NULL DEFAULT 0,
  expire_time BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS t_user_session_history (
  sid VARCHAR(32),
  uid INT,
  action VARCHAR(16),
  code INT,
  time BIGINT
);
INSERT INTO t_user(name, pass, level, resource, disabled) VALUES('admin', MD5('admin'), 'SYSADMIN', '1', 'N')
ON DUPLICATE KEY UPDATE pass=VALUES(pass), level=VALUES(level), resource=VALUES(resource), disabled=VALUES(disabled);
SELECT id, name, level, resource FROM t_user;
EOF
echo ""
echo "=== 2. 登录测试 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c /tmp/auth_cookie.txt --max-time 30 2>&1 | head -c 500
echo ""
echo "cookie:"
cat /tmp/auth_cookie.txt 2>/dev/null
echo ""
echo "=== 3. auth_status 测试（带 cookie） ==="
curl -s "http://127.0.0.1/d/auth?auth_target=auth_status" -b /tmp/auth_cookie.txt --max-time 30 2>&1 | head -c 500
echo ""
echo "=== 4. 错误密码测试 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=wrong" --max-time 30 2>&1 | head -c 500
echo ""
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
