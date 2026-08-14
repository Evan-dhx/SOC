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
        print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

# =====================================================================
# 深入诊断 auth CGI 崩溃
# =====================================================================
print("=" * 70)
print("深入诊断 auth CGI 崩溃")
print("=" * 70)

# ---- 1. 检查正确的错误日志路径 ----
print("\n--- 检查错误日志路径 ---")
run('ls -la /var/log/httpd/ly_error_log /etc/httpd/logs/ly_error_log 2>/dev/null', "错误日志文件")
run('tail -20 /var/log/httpd/ly_error_log 2>/dev/null', "var/log/httpd 错误日志")

# ---- 2. 读取 auth.cpp 完整 main 函数 ----
print("\n--- auth.cpp main 函数 ---")
out, _ = run('grep -n "int main" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "main 行号")
if out.strip():
    main_line = int(out.strip().split(':')[0])
    run(f'sed -n "{main_line-5},{main_line+50}p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "main 函数")

# ---- 3. 读取 dbc.cpp 数据库初始化代码 ----
print("\n--- dbc.cpp 数据库初始化 ---")
run('cat /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', "dbc.cpp 完整内容")

# ---- 4. 检查 define.h 中的 DB_CONF 和日志路径 ----
print("\n--- 检查 define.h ---")
run('grep -n "DB_CONF\\|LOG\\|log\\|SYSLOG\\|IDENT\\|/Server/log\\|/var/log" /root/SOC/ly_server_src/server/define.h 2>/dev/null | head -20', "define.h 关键定义")

# ---- 5. 以 apache 用户运行 auth (完整 CGI 环境) ----
print("\n--- 以 apache 用户运行 auth (完整 CGI 环境) ---")
# 清理日志
run('echo "" > /var/log/httpd/ly_error_log', "清理 var/log/httpd 日志")

# 完整 CGI 环境
full_cgi = (
    'QUERY_STRING="" '
    'REQUEST_METHOD=GET '
    'REQUEST_URI=/d/auth '
    'SCRIPT_NAME=/d/auth '
    'SCRIPT_FILENAME=/Server/www/d/auth '
    'PATH=/usr/bin:/bin '
    'HTTP_HOST=127.0.0.1 '
    'REMOTE_ADDR=127.0.0.1 '
    'SERVER_NAME=10.10.102.220 '
    'SERVER_PORT=80 '
    'SERVER_PROTOCOL=HTTP/1.1 '
    'HTTP_COOKIE="" '
    'GATEWAY_INTERFACE=CGI/1.1 '
    'LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib'
)

# 以 apache 运行
out, _ = run(f'su -s /bin/bash -c "env -i {full_cgi} /Server/www/d/auth" apache 2>&1', "apache 用户完整 CGI GET")

# ---- 6. 检查 auth 输出和错误 ----
print("\n--- 检查错误日志 ---")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "var/log/httpd 错误日志")
run('cat /etc/httpd/logs/ly_error_log 2>/dev/null', "etc/httpd/logs 错误日志")

# 检查 syslog
run('grep "auth" /var/log/messages 2>/dev/null | tail -5 || journalctl -t auth --no-pager -n 5 2>/dev/null || echo "无 syslog"', "syslog auth 错误")

# 检查 /Server/log
run('ls /Server/log/ 2>/dev/null && tail -5 /Server/log/*.log 2>/dev/null || echo "无 /Server/log"', "Server log")

# ---- 7. 检查数据库配置文件权限 ----
print("\n--- 检查数据库配置 ---")
run('ls -la /etc/my.cnf.d/gl.server.cnf 2>/dev/null', "gl.server.cnf 权限")
run('stat /etc/my.cnf.d/gl.server.cnf 2>/dev/null', "gl.server.cnf 详细")
run('su -s /bin/bash -c "cat /etc/my.cnf.d/gl.server.cnf" apache 2>&1', "apache 读取 gl.server.cnf")

# ---- 8. 检查 t_user 表 ----
print("\n--- 检查 t_user 表 ---")
run('mysql -u root -ppassword123 -e "SELECT * FROM t_user LIMIT 5;" server 2>/dev/null', "t_user 表内容")
run('mysql -u root -ppassword123 -e "SHOW COLUMNS FROM t_user;" server 2>/dev/null', "t_user 表结构")
run('mysql -u root -ppassword123 -e "SELECT * FROM t_user_session LIMIT 5;" server 2>/dev/null', "t_user_session 表")

# ---- 9. 检查 auth 是否可以连接数据库 ----
print("\n--- 测试数据库连接 ---")
# 用 apache 用户测试数据库连接
run('su -s /bin/bash -c "mysql -u root -ppassword123 -e \"SELECT 1;\" 2>&1" apache', "apache 用户 mysql 连接")

# ---- 10. strace auth (简化) ----
print("\n--- strace auth (文件访问) ---")
run(f'strace -f -e trace=openat,access su -s /bin/bash -c "env -i {full_cgi} /Server/www/d/auth" apache 2>&1 | grep -v "ENOENT\\|/proc\\|/sys\\|/usr/lib\\|/lib64\\|locale\\|charset\\|/dev/" | tail -30', "strace 文件访问")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
