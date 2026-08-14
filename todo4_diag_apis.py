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
        print(f"  STDERR: {err.strip()[:3000]}")
    return out, err

print("=" * 70)
print("诊断 feature / event_feature / ipinfo 错误")
print("=" * 70)

# ---- 1. 先登录获取 session ----
print("\n--- [1] 登录获取 session ---")
run('curl -s -c /tmp/cookies.txt -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "登录")

# ---- 2. 清理日志后单独测试 feature ----
print("\n--- [2] 测试 feature CGI ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" "http://127.0.0.1/d/feature" 2>&1', "GET feature")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" -X POST -d "op=get" "http://127.0.0.1/d/feature" 2>&1', "POST feature op=get")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "feature 错误日志")

# ---- 3. 测试 event_feature ----
print("\n--- [3] 测试 event_feature CGI ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" "http://127.0.0.1/d/event_feature" 2>&1', "GET event_feature")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" -X POST -d "op=get" "http://127.0.0.1/d/event_feature" 2>&1', "POST event_feature op=get")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "event_feature 错误日志")

# ---- 4. 测试 ipinfo ----
print("\n--- [4] 测试 ipinfo CGI ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" "http://127.0.0.1/d/ipinfo" 2>&1', "GET ipinfo 无参数")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" -X POST -d "op=get&ip=8.8.8.8" "http://127.0.0.1/d/ipinfo" 2>&1', "POST ipinfo with ip")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "ipinfo 错误日志")

# ---- 5. 检查 feature 源码看它需要什么参数 ----
print("\n--- [5] 检查 feature 源码 ---")
run('grep -n "int main" /root/SOC/ly_server_src/server/feature.cpp 2>/dev/null', "feature main 行号")
run('head -80 /root/SOC/ly_server_src/server/feature.cpp 2>/dev/null', "feature 源码头部")

# ---- 6. 检查 event_feature 源码 ----
print("\n--- [6] 检查 event_feature 源码 ---")
run('grep -n "int main" /root/SOC/ly_server_src/server/event_feature.cpp 2>/dev/null', "event_feature main 行号")
run('head -80 /root/SOC/ly_server_src/server/event_feature.cpp 2>/dev/null', "event_feature 源码头部")

# ---- 7. 检查 ipinfo 源码 ----
print("\n--- [7] 检查 ipinfo 源码 ---")
run('grep -n "open error\\|fopen\\|ifstream\\|open(" /root/SOC/ly_server_src/server/ipinfo.cpp 2>/dev/null | head -20', "ipinfo 文件操作")
run('grep -n "int main" /root/SOC/ly_server_src/server/ipinfo.cpp 2>/dev/null', "ipinfo main 行号")

# ---- 8. 直接以 CGI 环境运行 feature（绕过 httpd 重写）----
print("\n--- [8] 直接运行 feature CGI ---")
cgi_env = (
    'QUERY_STRING="op=get" '
    'REQUEST_METHOD=POST '
    'REQUEST_URI="/d/feature" '
    'SCRIPT_NAME="/d/feature" '
    'SCRIPT_FILENAME="/Server/www/d/feature" '
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
run(f'echo "op=get" | su -s /bin/bash -c "env -i {cgi_env} /Server/www/d/feature" apache 2>&1 | head -20', "直接运行 feature")

# ---- 9. 检查 feature 的 ldd 依赖 ----
print("\n--- [9] 检查 CGI 依赖 ---")
run('ldd /Server/www/d/feature 2>&1 | grep "not found"', "feature 依赖")
run('ldd /Server/www/d/event_feature 2>&1 | grep "not found"', "event_feature 依赖")
run('ldd /Server/www/d/ipinfo 2>&1 | grep "not found"', "ipinfo 依赖")

# ---- 10. 检查 feature 是否通过 auth 路由时的问题 ----
print("\n--- [10] 检查 auth 路由 feature 的方式 ---")
run('grep -n "feature" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null | head -20', "auth 中 feature 路由")

# ---- 11. 检查 geoinfo 为什么返回空 ----
print("\n--- [11] 检查 geoinfo ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" -X POST -d "op=get" "http://127.0.0.1/d/geoinfo" 2>&1', "POST geoinfo op=get")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "geoinfo 错误日志")

# ---- 12. 清理 ----
run('echo "=== TODO4 DIAG DONE $(date) ===" > /var/log/httpd/ly_error_log', "清理日志")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
