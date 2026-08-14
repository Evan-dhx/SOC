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
print("排查 code 300 与 session 验证")
print("=" * 70)

# ---- 1. 搜索 300 / CODE 相关定义 ----
print("\n--- [1] code 300 相关定义 ---")
run('grep -n "300\\|CODE_FAIL_SESSION\\|CODE_FAIL_AUTH\\|CODE_SUCCEED\\|CODE_FAIL_RETRY\\|#define CODE" /root/SOC/ly_server_src/server/auth.cpp', "code 定义")

# ---- 2. 查看 config 处理的完整代码 ----
print("\n--- [2] config 请求处理完整代码 ---")
run('sed -n "/else if.*auth_target.*config/,/else/p" /root/SOC/ly_server_src/server/auth.cpp | head -80', "config 处理段")

# ---- 3. 查看 auth.cpp 中 main 函数完整逻辑 ----
print("\n--- [3] main 函数完整流程 ---")
run('sed -n "/int main/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp | head -200', "main 函数")

# ---- 4. 查看 check_session 被调用的地方 ----
print("\n--- [4] check_session 调用位置 ---")
run('grep -n "check_session\\|update_session\\|get_session" /root/SOC/ly_server_src/server/auth.cpp', "session 调用")

# ---- 5. 查看 auth_status 的完整逻辑 ----
print("\n--- [5] auth_status 处理 ---")
run('sed -n "/auth_status/,/break\\|^[[:space:]]*}\\|else/p" /root/SOC/ly_server_src/server/auth.cpp | head -40', "auth_status 处理")

# ---- 7. 上传 Python 脚本并执行会话测试 ----
print("\n--- [7] 上传并执行 session 测试 ---")
sftp = c.open_sftp()
with sftp.file('/tmp/test_session.py', 'w') as f:
    f.write("""import urllib.request, http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = b"auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3"
req = urllib.request.Request("http://127.0.0.1/d/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
print("Login body:", resp.read().decode())
print("Cookies after login:")
for c in cj:
    print("  %s=%s domain=%s path=%s" % (c.name, c.value, c.domain, c.path))
data2 = b"auth_target=config&type=user&op=GET"
req2 = urllib.request.Request("http://127.0.0.1/d/config", data=data2, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp2 = opener.open(req2)
print("Config body:", resp2.read().decode()[:500])
""")
sftp.close()
run('python3 /tmp/test_session.py 2>&1', "session 测试")

# ---- 8. 检查前端存储的登录状态 key ----
print("\n--- [8] 前端存储的登录状态 key ---")
run('grep -oP "ly-user.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "ly-user")
run('grep -oP "ly-auth.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "ly-auth")
run('grep -oP "localStorage.{0,100}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "localStorage")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)