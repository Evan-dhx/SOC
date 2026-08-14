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
print("检查前端登录请求格式")
print("=" * 70)

# ---- 1. 搜索 main.js 中 login 相关代码 ----
print("\n--- [1] main.js 中 login 相关代码 ---")
run('grep -o ".\\{0,80\\}login.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -20', "login 相关")

# ---- 2. 搜索 auth_user / auth_pass ----
print("\n--- [2] auth_user / auth_pass 相关 ---")
run('grep -o ".\\{0,100\\}auth_user.\\{0,100\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "auth_user")
run('grep -o ".\\{0,100\\}auth_pass.\\{0,100\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "auth_pass")

# ---- 3. 搜索 POST 请求代码 ----
print("\n--- [3] POST / fetch 相关 ---")
run('grep -o ".\\{0,60\\}fetch(.\\{0,120\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "fetch 调用")

# ---- 4. 搜索 login API 调用 ----
print("\n--- [4] /d/login 或 /login 相关 ---")
run('grep -o ".\\{0,80\\}/d/login.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "/d/login")
run('grep -o ".\\{0,80\\}login.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -20', "login 引用")

# ---- 5. 搜索 JSON.stringify / FormData ----
print("\n--- [5] 请求体格式 ---")
run('grep -o ".\\{0,60\\}JSON.stringify.\\{0,60\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "JSON.stringify")
run('grep -o ".\\{0,60\\}FormData.\\{0,60\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "FormData")
run('grep -o ".\\{0,60\\}URLSearchParams.\\{0,60\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "URLSearchParams")

# ---- 6. 搜索 content-type / headers ----
print("\n--- [6] Content-Type 相关 ---")
run('grep -o ".\\{0,80\\}Content-Type.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "Content-Type")
run('grep -o ".\\{0,80\\}content-type.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "content-type")

# ---- 7. 搜索 auth_target ----
print("\n--- [7] auth_target 相关 ---")
run('grep -o ".\\{0,80\\}auth_target.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "auth_target")

# ---- 8. 搜索登录函数完整代码 ----
print("\n--- [8] 登录函数上下文 ---")
# 搜索包含 auth_user 和 auth_pass 的更大上下文
run('grep -oP ".{0,200}auth_user.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "auth_user 上下文")

# ---- 9. 用不同格式测试 curl 登录 ----
print("\n--- [9] 不同格式 curl 登录测试 ---")
# 模拟浏览器 POST /d/login
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/login 2>&1', "POST /d/login (form)")
run('curl -s -X POST -H "Content-Type: application/json" -d \'{"auth_user":"admin","auth_pass":"admin","auth_target":"login"}\' http://127.0.0.1/d/login 2>&1', "POST /d/login (json)")
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin" http://127.0.0.1/d/login 2>&1', "POST /d/login (no target)")

# ---- 10. 检查 auth.cpp 中如何读取参数 ----
print("\n--- [10] auth.cpp 参数读取 ---")
run('grep -n "cgi(\\|getenv\\|QUERY_STRING\\|CONTENT_TYPE\\|auth_user\\|auth_pass\\|auth_target" /root/SOC/ly_server_src/server/auth.cpp | head -30', "参数读取")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
