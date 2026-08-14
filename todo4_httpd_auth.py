import paramiko
import sys
import time

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
# 待办 4: httpd auth CGI 运行环境检查与修复
# =====================================================================
print("=" * 70)
print("待办 4: httpd auth CGI 运行环境检查与修复")
print("=" * 70)

# ---- 4.1 检查 httpd CGI 配置 ----
print("\n" + "-" * 50)
print("[4.1] 检查 httpd CGI 配置")
print("-" * 50)

# 检查 httpd 配置文件
run('ls /etc/httpd/conf.d/*.conf 2>/dev/null', "httpd 配置文件")
run('cat /etc/httpd/conf.d/ly.conf 2>/dev/null || cat /etc/httpd/conf.d/luying.conf 2>/dev/null || echo "未找到 ly 配置"', "ly 配置内容")

# 搜索 CGI 相关配置
run('grep -r "ScriptAlias\\|AddHandler\\|Options.*ExecCGI\\|/Server/www" /etc/httpd/conf.d/ 2>/dev/null | head -20', "CGI 配置")
run('grep -r "ScriptAlias\\|AddHandler\\|Options.*ExecCGI\\|/Server/www" /etc/httpd/conf/httpd.conf 2>/dev/null | head -20', "主配置 CGI")

# 检查 suexec 配置
run('ls -la /usr/sbin/suexec 2>/dev/null', "suexec 二进制")
run('grep -r "SuexecUserGroup\\|suexec" /etc/httpd/ 2>/dev/null | head -10', "suexec 配置")

# 检查 /Server/www/d 目录权限
run('ls -la /Server/www/d/ | head -20', "/Server/www/d 目录")
run('ls -ld /Server/www/d/ 2>/dev/null', "目录权限")

# ---- 4.2 检查 auth CGI 的依赖和运行 ----
print("\n" + "-" * 50)
print("[4.2] 检查 auth CGI 依赖和运行")
print("-" * 50)

# ldd 依赖
run('ldd /Server/www/d/auth 2>/dev/null', "auth ldd")

# 检查 auth 源码 - 看它如何调用 topn
print("\n--- auth 源码中的 topn 调用 ---")

# ---- 4.3 模拟 CGI 环境测试 auth ----
print("\n" + "-" * 50)
print("[4.3] 模拟 CGI 环境测试 auth")
print("-" * 50)

# 先清理旧错误日志
run('echo "" > /etc/httpd/logs/ly_error_log', "清理 httpd 错误日志")

# 模拟 CGI 环境 - GET 请求
print("\n--- 模拟 GET 请求 (无参数) ---")
cgi_env = 'QUERY_STRING="" REQUEST_METHOD=GET REQUEST_URI=/d/auth SCRIPT_NAME=/d/auth SCRIPT_FILENAME=/Server/www/d/auth PATH=/usr/bin:/bin'
out, _ = run(f'env -i {cgi_env} /Server/www/d/auth 2>&1 | head -10', "auth GET (无参数)")

# 模拟 CGI 环境 - POST 登录请求
print("\n--- 模拟 POST 登录请求 ---")
post_data = 'username=admin&password=admin'
cgi_env_post = f'QUERY_STRING="" REQUEST_METHOD=POST REQUEST_URI=/d/auth SCRIPT_NAME=/d/auth SCRIPT_FILENAME=/Server/www/d/auth PATH=/usr/bin:/bin CONTENT_LENGTH={len(post_data)}'
out, _ = run(f'echo -n "{post_data}" | env -i {cgi_env_post} /Server/www/d/auth 2>&1 | head -20', "auth POST 登录")

# ---- 4.4 通过 HTTP 请求测试 ----
print("\n" + "-" * 50)
print("[4.4] 通过 HTTP 请求测试 auth")
print("-" * 50)

# 用 curl 测试
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}\\n" http://127.0.0.1/d/auth 2>&1', "auth HTTP GET")
run('curl -s http://127.0.0.1/d/auth 2>&1 | head -10', "auth HTTP GET 内容")

# POST 登录测试
run('curl -s -X POST -d "username=admin&password=admin" http://127.0.0.1/d/auth 2>&1 | head -20', "auth HTTP POST 登录")

# ---- 4.5 检查 httpd 错误日志 ----
print("\n" + "-" * 50)
print("[4.5] 检查 httpd 错误日志 (测试后)")
print("-" * 50)

run('cat /etc/httpd/logs/ly_error_log 2>/dev/null', "httpd 错误日志 (测试后)")

# ---- 4.6 检查 auth 源码 ----
print("\n" + "-" * 50)
print("[4.6] 检查 auth 源码逻辑")
print("-" * 50)

run('grep -n "topn\\|exec\\|system\\|popen\\|Location\\|redirect" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -20', "auth 源码关键行")
run('head -80 /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "auth 源码头部")

# ---- 4.7 检查 httpd 进程和端口 ----
print("\n" + "-" * 50)
print("[4.7] 检查 httpd 进程和端口")
print("-" * 50)

run('ps aux | grep httpd | grep -v grep | head -5', "httpd 进程")
run('ss -tlnp | grep -E "80|443" 2>/dev/null', "监听端口")

# ---- 4.8 总结 ----
print("\n" + "-" * 50)
print("[4.8] 待办 4 总结")
print("-" * 50)

# 重新检查错误日志
out, _ = run('wc -l /etc/httpd/logs/ly_error_log 2>/dev/null', "错误日志行数")
out2, _ = run('grep -c "error\\|Error" /etc/httpd/logs/ly_error_log 2>/dev/null', "错误行数")
print(f"  httpd 错误日志: {out.strip()} 总行, {out2.strip()} 错误行")

# 检查 auth 是否产生新错误
out3, _ = run('grep "auth" /etc/httpd/logs/ly_error_log 2>/dev/null | tail -5', "auth 相关错误")
if out3.strip():
    print(f"  auth 相关错误:\n{out3.strip()}")
else:
    print("  auth 相关错误: 无 (测试后无新错误)")

c.close()
print("\n" + "=" * 70)
print("待办 4 检查完成!")
print("=" * 70)
