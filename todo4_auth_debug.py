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
        print(out.strip()[:4000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:500]}")
    return out, err

# =====================================================================
# 深入诊断 auth CGI 崩溃原因
# =====================================================================
print("=" * 70)
print("深入诊断 auth CGI 崩溃原因")
print("=" * 70)

# ---- 1. 检查 auth 源码 main 函数 ----
print("\n--- auth 源码 main 函数和初始化 ---")
run('grep -n "int main\\|Cgicc\\|cgi\\|getEnvironment\\|DB_CONF\\|sql.*open\\|dbc\\|http.*header\\|Content-Type" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -30', "auth 关键行")

# 读取 auth.cpp 的 main 函数部分
run('grep -n "int main" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "main 函数位置")

# ---- 2. 检查 suexec 用户 ----
print("\n--- 检查 CGI 运行用户 ---")
run('grep -r "SuexecUserGroup\\|User\\|Group" /etc/httpd/conf.d/ly_server.conf 2>/dev/null', "suexec 用户配置")
run('grep -r "User\\|Group" /etc/httpd/conf/httpd.conf 2>/dev/null | grep -v "^#" | head -5', "httpd 用户")

# ---- 3. 以 apache 用户运行 auth ----
print("\n--- 以 apache 用户模拟 CGI 环境 ---")
# 清理错误日志
run('echo "" > /etc/httpd/logs/ly_error_log', "清理日志")

# 用 su - apache 运行
cgi_env = 'QUERY_STRING="" REQUEST_METHOD=GET REQUEST_URI=/d/auth SCRIPT_NAME=/d/auth SCRIPT_FILENAME=/Server/www/d/auth PATH=/usr/bin:/bin HTTP_HOST=127.0.0.1'
run(f'su -s /bin/bash -c "env -i {cgi_env} /Server/www/d/auth" apache 2>&1 | head -20', "apache 用户 CGI GET")

# ---- 4. 检查数据库配置可读性 ----
print("\n--- 检查数据库配置可读性 ---")
run('ls -la /etc/my.cnf.d/gl.server.cnf 2>/dev/null', "gl.server.cnf 权限")
run('cat /etc/my.cnf.d/gl.server.cnf 2>/dev/null', "gl.server.cnf 内容")
run('su -s /bin/bash -c "cat /etc/my.cnf.d/gl.server.cnf" apache 2>&1', "apache 能否读取")

# 检查 auth 用什么方式连接数据库
run('grep -n "DB_CONF\\|gl.server\\|my.cnf\\|sql.*open\\|connect\\|read.*conf\\|dbc.*Init\\|DBC" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -20', "auth 数据库连接代码")
run('grep -n "DB_CONF\\|gl.server\\|my.cnf\\|sql.*open\\|connect\\|read.*conf\\|dbc.*Init\\|DBC" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null | head -20', "dbc 数据库连接代码")

# ---- 5. 检查 auth 是否需要 session 目录 ----
print("\n--- 检查 session/临时目录 ---")
run('grep -n "session\\|tmp\\|temp\\|/var\\|/Server.*log\\|LOG_FILE\\|log_" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -15', "session/日志相关")

# 检查 /Server/log 目录
run('ls -la /Server/log/ 2>/dev/null', "/Server/log 目录")
run('ls -la /var/log/luying/ 2>/dev/null || echo "无 /var/log/luying"', "/var/log/luying")

# ---- 6. 直接 strace auth ----
print("\n--- strace auth 以确定崩溃点 ---")
run('which strace 2>/dev/null', "strace 可用性")
out, _ = run('strace -f -e trace=openat,access,execve su -s /bin/bash -c "env -i QUERY_STRING=\"\" REQUEST_METHOD=GET /Server/www/d/auth" apache 2>&1 | tail -30', "strace auth", timeout=30)

# ---- 7. 检查 auth 源码完整流程 ----
print("\n--- auth 源码完整 main 函数 ---")
# 找到 main 函数行号
out, _ = run('grep -n "int main" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "main 行号")
if out.strip():
    main_line = int(out.strip().split(':')[0])
    # 读取 main 函数
    run(f'sed -n "{main_line},{main_line+100}p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "main 函数内容")

# ---- 8. 检查 cgicc 环境要求 ----
print("\n--- 检查 cgicc 环境 ---")
run('grep -n "Cgicc\\|getEnvironment\\|getCgiEnvironment\\|HTTP_COOKIE\\|SERVER_NAME\\|REMOTE_ADDR" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -15', "cgicc 环境变量使用")

# 检查 auth 是否需要 HTTP_COOKIE
run('grep -n "COOKIE\\|cookie\\|sid\\|session" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -15', "cookie/session 相关")

# ---- 9. 检查 ly_server.conf 完整配置 ----
print("\n--- ly_server.conf 完整配置 ---")
run('cat /etc/httpd/conf.d/ly_server.conf 2>/dev/null', "ly_server.conf")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
