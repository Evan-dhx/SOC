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
print("诊断 admin 登录问题")
print("=" * 70)

# ---- 1. 检查 t_user 表完整内容和密码 ----
print("\n--- [1] 检查 t_user 表 ---")
run('mysql -u root -ppassword123 -e "SELECT id,username,password,role FROM t_user;" server 2>/dev/null', "t_user 表内容")
run('mysql -u root -ppassword123 -e "SHOW COLUMNS FROM t_user;" server 2>/dev/null', "t_user 表结构")

# ---- 2. 检查 auth.cpp 中 login 处理逻辑 ----
print("\n--- [2] auth.cpp login 处理逻辑 ---")
run('grep -n "login\\|auth_user\\|auth_pass\\|password\\|passwd\\|SESSION" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -40', "auth.cpp login 相关行")

# ---- 3. 查看 auth.cpp process 函数 ----
print("\n--- [3] auth.cpp process 函数 ---")
run('grep -n "process\\|CODE_TARGET\\|login" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -20', "process 和 login 行号")

# 找到 process 函数
out, _ = run('grep -n "int process" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "process 函数行号")
if out.strip():
    line = int(out.strip().split(':')[0])
    run(f'sed -n "{line},{line+100}p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "process 函数内容")

# ---- 4. 查看 login 处理的具体代码 ----
print("\n--- [4] login 处理代码 ---")
out2, _ = run('grep -n "login" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "login 行号")
if out2.strip():
    for line_info in out2.strip().split('\n')[:5]:
        ln = int(line_info.split(':')[0])
        run(f'sed -n "{ln-2},{ln+30}p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', f"login 行 {ln} 上下文")

# ---- 5. 详细 curl 测试 admin/admin ----
print("\n--- [5] 详细 curl 测试 admin/admin ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "curl POST admin/admin 详细")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")

# ---- 6. 测试其他用户 ----
print("\n--- [6] 测试其他用户 ---")
run('curl -s -X POST -d "auth_user=analyser&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "analyser/admin")
run('curl -s -X POST -d "auth_user=admin&auth_pass=password123&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin/password123")

# ---- 7. 检查前端登录页面的请求格式 ----
print("\n--- [7] 前端登录页面 ---")
run('find /Server/www/ui -name "*.js" -exec grep -l "login\\|auth_user\\|auth_pass" {} \\; 2>/dev/null | head -10', "包含登录逻辑的 JS 文件")
run('find /Server/www/ui -name "*.js" -exec grep -l "auth_target" {} \\; 2>/dev/null | head -10', "包含 auth_target 的 JS 文件")

# 检查前端配置文件
run('cat /Server/www/ui/app-config/config.js 2>/dev/null', "前端配置")

# 检查前端 API 调用
run('grep -rn "auth_user\\|auth_pass\\|login\\|/d/auth" /Server/www/ui/static/js/ 2>/dev/null | head -20', "前端 JS 中的登录调用")

# ---- 8. 检查密码是否是明文或哈希 ----
print("\n--- [8] 检查密码存储方式 ---")
run('mysql -u root -ppassword123 -e "SELECT username,password FROM t_user WHERE username=\'admin\';" server 2>/dev/null', "admin 密码值")
run('grep -n "md5\\|sha\\|hash\\|encrypt\\|password\\|passwd" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -20', "auth.cpp 密码处理")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
