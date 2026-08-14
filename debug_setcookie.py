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
print("深入排查 Set-Cookie 问题")
print("=" * 70)

# ---- 1. 查看 auth.cpp 完整的 login 处理逻辑 ----
print("\n--- [1] login 处理完整代码 ---")
run('sed -n "/auth_target.*login/,/break/p" /root/SOC/ly_server_src/server/auth.cpp | head -100', "login 处理")

# ---- 2. 查看 auth.cpp 的 main 函数 ----
print("\n--- [2] main 函数中 session/cookie 设置 ---")
run('grep -n "cookie\\|Cookie\\|SESSION_ID\\|header.set" /root/SOC/ly_server_src/server/auth.cpp', "cookie 设置相关")

# ---- 3. 用 curl 模拟浏览器完整流程（检查 Set-Cookie 细节） ----
print("\n--- [3] curl 完整会话测试 ---")
run('rm -f /tmp/session_cookies.txt', "清理 cookie 文件")

# 第一次请求 - 登录，保存 cookie
_, stdout, _ = c.exec_command(
    'curl -s -v -c /tmp/session_cookies.txt '
    '-H "Accept: application/json, text/plain, */*" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://127.0.0.1/d/login 2>&1',
    timeout=30
)
print("登录请求（无 auth_target）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# 查看 cookie 文件
_, stdout, _ = c.exec_command('cat /tmp/session_cookies.txt 2>/dev/null', timeout=10)
print("\n登录后的 cookie 文件:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# 第二次请求 - 用 cookie 请求 config
_, stdout, _ = c.exec_command(
    'curl -s -v -b /tmp/session_cookies.txt '
    '-H "Accept: application/json, text/plain, */*" '
    '-d "auth_target=config&type=user&op=GET" '
    'http://127.0.0.1/d/config 2>&1',
    timeout=30
)
print("\nconfig 请求（带 cookie）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# ---- 4. 检查 auth.cpp 中是否对 POST body 的 auth_target 和 URL 参数有不同处理 ----
print("\n--- [4] auth.cpp 中参数读取方式 ---")
run('head -260 /root/SOC/ly_server_src/server/auth.cpp | tail -80', "参数读取代码")

# ---- 5. 检查浏览器发送格式的请求是否也会得到 Set-Cookie ----
print("\n--- [5] 用浏览器相同请求格式测试 ---")
# 没有 auth_target 但通过 RewriteRule 添加
_, stdout, _ = c.exec_command(
    'curl -s -v -c /tmp/session_cookies2.txt '
    '-H "Accept: application/json, text/plain, */*" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    '-H "Origin: http://10.10.102.220" '
    '-H "Referer: http://10.10.102.220/" '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://10.10.102.220/d/login 2>&1',
    timeout=30
)
print("通过 10.10.102.220（模拟浏览器）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# ---- 6. 检查响应头（仅看响应头） ----
_, stdout, _ = c.exec_command(
    'curl -s -D - -o /dev/null '
    '-H "Accept: application/json, text/plain, */*" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    '-H "Origin: http://10.10.102.220" '
    '-H "Referer: http://10.10.102.220/" '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://10.10.102.220/d/login 2>&1',
    timeout=30
)
print("\n响应头（仅 headers）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)