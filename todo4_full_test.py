import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:5000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:5000]}")
    return out, err

print("=" * 70)
print("验证 auth CGI 完整功能链")
print("=" * 70)

# ---- 1. POST 登录获取 session ----
print("\n--- [1] POST 登录 ---")
out, _ = run('curl -s -c /tmp/cookies.txt -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "登录响应")
run('cat /tmp/cookies.txt 2>/dev/null', "Cookie 文件")

# 提取 SESSION_ID
out2, _ = run('grep SESSION_ID /tmp/cookies.txt 2>/dev/null | awk "{print \\$7}"', "SESSION_ID")
session_id = out2.strip()
print(f"  Session ID: {session_id}")

# ---- 2. 使用 session 访问各个 API ----
print("\n--- [2] 使用 session 访问 API ---")

apis = ['auth_status', 'mo', 'topn', 'event', 'config', 'bwlist', 'feature',
        'internalip', 'ipinfo', 'portinfo', 'locinfo', 'geoinfo', 'event_feature']

for api in apis:
    out, _ = run(f'curl -s -b /tmp/cookies.txt "http://127.0.0.1/d/auth?auth_target={api}" 2>&1 | head -5', f"GET {api}")
    # 判断是否成功
    if out.strip() and '500' not in out and 'Internal Server Error' not in out:
        print(f"  {api:20s} OK  ({out.strip()[:80]})")
    else:
        print(f"  {api:20s} FAIL ({out.strip()[:80]})")

# ---- 3. 使用 session POST 操作 ----
print("\n--- [3] 使用 session POST 操作 ---")
# 查询设备列表
run('curl -s -b /tmp/cookies.txt -X POST -d "auth_target=mo&op=get" http://127.0.0.1/d/auth 2>&1 | head -5', "POST mo get")
# 查询事件
run('curl -s -b /tmp/cookies.txt -X POST -d "auth_target=event&op=get" http://127.0.0.1/d/auth 2>&1 | head -5', "POST event get")

# ---- 4. 测试前端页面 ----
print("\n--- [4] 测试前端页面 ---")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ 2>&1', "首页")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ui/ 2>&1', "UI 页面")
run('curl -s http://127.0.0.1/ 2>&1 | head -10', "首页内容")

# ---- 5. 检查错误日志 ----
print("\n--- [5] 检查错误日志 ---")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "var/log/httpd 错误日志")

# ---- 6. 清理旧日志并标记 ----
print("\n--- [6] 清理并标记日志 ---")
run('echo "=== AUTH VERIFY DONE $(date) ===" > /var/log/httpd/ly_error_log', "清理日志")

c.close()
print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
