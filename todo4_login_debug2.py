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
        print(out.strip()[:8000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:3000]}")
    return out, err

print("=" * 70)
print("深入检查登录问题")
print("=" * 70)

# ---- 1. 用正确字段名查询 t_user 表 ----
print("\n--- [1] t_user 表实际数据 ---")
run('mysql -u root -ppassword123 -e "SELECT id,name,pass,level,disabled,lockedtime FROM t_user;" server 2>/dev/null', "t_user 全部用户")
run('mysql -u root -ppassword123 -e "SELECT id,name,pass,level FROM t_user WHERE name=\'admin\';" server 2>/dev/null', "admin 用户")

# ---- 2. 检查 md5 值 ----
print("\n--- [2] 检查密码 MD5 ---")
run('echo -n "admin" | md5sum', "admin 的 MD5")
run('echo -n "password123" | md5sum', "password123 的 MD5")

# ---- 3. 查看 do_login 函数完整代码 ----
print("\n--- [3] do_login 函数完整代码 ---")
run('sed -n "244,330p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "do_login 函数")

# ---- 4. 检查 auth.cpp 中如何验证密码 ----
print("\n--- [4] 密码验证逻辑 ---")
run('grep -n "md5\\|MD5\\|pass\\|password\\|verify\\|check\\|compare\\|SELECT.*FROM.*t_user" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "密码验证相关")
run('grep -n "md5\\|MD5\\|pass\\|password\\|verify\\|check\\|compare\\|SELECT.*FROM.*t_user" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', "dbc.cpp 密码验证相关")

# ---- 5. 查看 dbc.cpp 中的用户验证函数 ----
print("\n--- [5] dbc.cpp 用户验证 ---")
run('grep -n "login\\|verify\\|check_user\\|auth\\|t_user\\|pass" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null | head -20', "dbc.cpp 用户验证函数")
out, _ = run('grep -n "check_user\\|verify_user\\|user_login\\|login" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', "查找用户验证函数")
if out.strip():
    for line_info in out.strip().split('\n')[:3]:
        ln = int(line_info.split(':')[0])
        run(f'sed -n "{ln-3},{ln+40}p" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', f"dbc.cpp 行 {ln} 上下文")

# ---- 6. 检查前端登录请求格式 ----
print("\n--- [6] 前端登录请求 ---")
# 搜索前端 JS 中登录相关的代码
run('grep -o "auth_user[^']*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "前端 auth_user")
run('grep -o "auth_pass[^']*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "前端 auth_pass")
run('grep -o "auth_target[^']*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "前端 auth_target")
run('grep -o "login[^\"]*login" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "前端 login 调用")

# ---- 7. 搜索前端登录组件 ----
print("\n--- [7] 前端登录组件 ---")
run('grep -o ".\\{0,50\\}auth_user.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "auth_user 上下文")
run('grep -o ".\\{0,80\\}auth_pass.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "auth_pass 上下文")
run('grep -o ".\\{0,50\\}auth_target=login.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "auth_target=login 上下文")

# ---- 8. 浏览器实际请求测试 ----
print("\n--- [8] 模拟前端请求格式 ---")
# 前端可能使用 JSON 格式
run('curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "form-urlencoded 格式")
run('curl -s -X POST -H "Content-Type: application/json" -d \'{"auth_user":"admin","auth_pass":"admin","auth_target":"login"}\' http://127.0.0.1/d/auth 2>&1', "JSON 格式")
# 前端可能通过 URL 参数
run('curl -s -X POST "http://127.0.0.1/d/auth?auth_target=login" -d "auth_user=admin&auth_pass=admin" 2>&1', "auth_target 在 URL 中")

# ---- 9. 检查 httpd 是否监听正确端口 ----
print("\n--- [9] 检查 httpd 监听 ---")
run('grep -n "Listen" /etc/httpd/conf/httpd.conf 2>/dev/null | head -5', "httpd.conf Listen")
run('grep -n "Listen" /etc/httpd/conf.d/ly_server.conf 2>/dev/null', "ly_server.conf Listen")
run('ss -tlnp | grep httpd 2>/dev/null', "httpd 监听端口")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
