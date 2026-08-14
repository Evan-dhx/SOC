import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=30):
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label: print(f"[{label}]")
    if out.strip(): print(out.strip()[:5000])
    if err.strip(): print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("修复 Cookie Version=1 问题 + 验证")
print("=" * 70)

# ---- 1. 在 httpd 中修改 Set-Cookie，移除 Version=1 ----
print("\n--- [1] 修改 httpd 配置 ---")
# 添加 Header edit 指令
run('grep -c "Header edit Set-Cookie" /etc/httpd/conf.d/ly_server.conf', "检查是否已有该配置")

run('''
sed -i '/^[[:space:]]*# Set LD_LIBRARY_PATH/i Header edit Set-Cookie "^(SESSION_ID=[^;]+); Version=1" "$1"' /etc/httpd/conf.d/ly_server.conf
''', "添加 Header edit")

# ---- 2. 备份并重启 httpd ----
print("\n--- [2] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启 httpd")

# ---- 3. 验证 Set-Cookie 已去除 Version=1 ----
print("\n--- [3] 验证 Set-Cookie ---")
_, stdout, _ = c.exec_command(
    'curl -s -D - -o /dev/null -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://127.0.0.1/d/login 2>&1',
    timeout=30
)
print("登录响应头:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# ---- 4. 验证完整流程 ----
_, stdout, _ = c.exec_command(
    'curl -s -c /tmp/test_new_cookie.txt -D - -o /dev/null -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://127.0.0.1/d/login 2>&1',
    timeout=30
)
print("\n登录响应头（新配置）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

_, stdout, _ = c.exec_command('cat /tmp/test_new_cookie.txt 2>/dev/null', timeout=10)
print("\ncookie 文件:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# ---- 5. 完整流验证 ----
print("\n--- [5] 完整流验证 ---")
sftp = c.open_sftp()
with sftp.file('/tmp/test_flow2.py', 'w') as f:
    f.write("""import urllib.request, http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
# Pre-login
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
try: opener.open(req)
except: pass
# Login
data = b"auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3"
req = urllib.request.Request("http://127.0.0.1/d/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
print("Login:", resp.read().decode())
# Config after login
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
body = resp.read().decode()
print("Config after login:", body[:200])
print("Has event data:", "event_type" in body)
# User config
data = b"auth_target=config&type=user&op=GET"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
body = resp.read().decode()
print("User config has admin:", "admin" in body)
""")
sftp.close()
run('python3 /tmp/test_flow2.py 2>&1', "完整流验证")

# ---- 6. 测试通过 10.10.102.220 访问 ----
print("\n--- [6] 通过外部 IP 测试 ---")
_, stdout, _ = c.exec_command(
    'curl -s -D - -o /dev/null -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://10.10.102.220/d/login 2>&1',
    timeout=30
)
print("通过 10.10.102.220 访问的 Set-Cookie:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

c.close()
print("\n" + "=" * 70)
print("修复完成!")
print("=" * 70)