import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:8000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("诊断 session 验证问题")
print("=" * 70)

# ---- 1. 检查 auth.cpp session 验证逻辑 ----
print("\n--- [1] auth.cpp session 验证代码 ---")
run('grep -n "SESSION_ID\\|session\\|getCookie\\|HTTPCookie\\|check_session\\|get_session\\|update_session" /root/SOC/ly_server_src/server/auth.cpp | head -40', "session 相关代码")

# ---- 2. 检查 auth.cpp 中 check_session / get_session 函数 ----
print("\n--- [2] session 验证函数 ---")
run('grep -n "check_session\\|get_session" /root/SOC/ly_server_src/server/auth.cpp', "session 函数位置")
run('sed -n "/check_session\\|get_session/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -80', "session 函数内容")

# ---- 3. curl 模拟完整登录流程 ----
print("\n--- [3] 模拟完整登录流程 ---")
# 第一步：发送登录请求，保存 cookie
_, stdout, _ = c.exec_command(
    'curl -s -v -c /tmp/cookies.txt -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3&auth_target=login" '
    'http://127.0.0.1/d/login 2>&1',
    timeout=30
)
out = stdout.read().decode('utf-8', errors='replace')
print("登录响应:")
print(out[:3000])

# 第二步：查看保存的 cookie
_, stdout, _ = c.exec_command('cat /tmp/cookies.txt 2>/dev/null', timeout=10)
out = stdout.read().decode('utf-8', errors='replace')
print("\nCookie 文件:")
print(out[:2000])

# 第三步：使用 cookie 发送 config 请求
_, stdout, _ = c.exec_command(
    'curl -s -b /tmp/cookies.txt -X POST '
    '-d "auth_target=config&type=user&op=GET" '
    'http://127.0.0.1/d/config 2>&1',
    timeout=30
)
out = stdout.read().decode('utf-8', errors='replace')
print("\n带 Cookie 的 config 请求:")
print(out[:2000])

# 第四步：使用 cookie 发送 config 请求（无参数）
_, stdout, _ = c.exec_command(
    'curl -s -b /tmp/cookies.txt http://127.0.0.1/d/config 2>&1',
    timeout=30
)
out = stdout.read().decode('utf-8', errors='replace')
print("\n带 Cookie 的 GET config:")
print(out[:2000])

# ---- 4. 检查 t_user_session 表 ----
print("\n--- [4] t_user_session 表 ---")
run('mysql -u root -ppassword123 -e "SELECT * FROM t_user_session;" server 2>/dev/null', "session 表")

# ---- 5. 检查登录后 config request 的 HTTP 日志 ----
print("\n--- [5] httpd 日志（清除后重测） ---")
run('echo "" > /var/log/httpd/ly_access_log; echo "" > /var/log/httpd/ly_error_log', "清空日志")
# 模拟完整浏览器流程
run('curl -s -c /tmp/cookies2.txt -X POST -d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3&auth_target=login" http://127.0.0.1/d/login -o /dev/null -w "LOGIN_CODE=%{http_code}" 2>&1', "登录")
run('curl -s -b /tmp/cookies2.txt http://127.0.0.1/d/config -o /dev/null -w "CONFIG_CODE=%{http_code}" 2>&1', "config 请求")
run('tail -20 /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")
run('tail -10 /var/log/httpd/ly_access_log 2>/dev/null', "访问日志")

# ---- 6. 检查 auth.cpp 中 config 请求的 session 验证 ----
print("\n--- [6] config 请求处理代码 ---")
run('sed -n "/auth_target.*config/,/break\\|^[[:space:]]*}/p" /root/SOC/ly_server_src/server/auth.cpp | head -60', "config 处理")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)