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
print("诊断 auth CGI: 检查 httpd CGI 环境和数据库连接")
print("=" * 70)

# ---- 1. 创建测试 CGI 打印环境变量 ----
print("\n--- [1] 创建测试 CGI ---")
test_cgi = '''#!/bin/bash
echo "Content-Type: text/plain"
echo ""
echo "=== CGI Environment ==="
env | sort
'''
run(f"cat > /Server/www/d/testenv << 'CGIEOF'\n{test_cgi}CGIEOF", "创建 testenv CGI")
run('chmod +x /Server/www/d/testenv', "设置权限")

# 通过 httpd 访问
print("\n--- httpd 传递的 CGI 环境变量 ---")
run('curl -s http://127.0.0.1/d/testenv 2>&1', "testenv HTTP 响应")

# ---- 2. 检查 dbc.h 中的数据库宏定义 ----
print("\n--- [2] 检查 dbc.h 数据库宏定义 ---")
run('cat /root/SOC/ly_server_src/server/dbc.h 2>/dev/null', "dbc.h 内容")
run('grep -rn "SERVER_DB_USER\\|SERVER_DB_NAME\\|SERVER_DB_GROUP" /root/SOC/ly_server_src/ 2>/dev/null | head -10', "数据库宏定义")

# ---- 3. 检查 define.h 完整内容 ----
print("\n--- [3] define.h 完整内容 ---")
run('cat /root/SOC/ly_server_src/server/define.h 2>/dev/null', "define.h")

# ---- 4. 以正确的 CGI 环境测试 auth ----
print("\n--- [4] 以正确 CGI 环境测试 auth ---")

# 先清理日志
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")

# 用 httpd 提供的完整环境运行
run('curl -v http://127.0.0.1/d/auth 2>&1', "curl auth 详细输出")

# POST 登录
run('curl -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "curl auth POST 登录")

# ---- 5. 检查错误日志 ----
print("\n--- [5] 检查错误日志 ---")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "var/log/httpd 错误日志")
run('journalctl -t auth --no-pager -n 3 2>/dev/null || echo "无 journalctl"', "journalctl auth")

# ---- 6. 检查 SCRIPT_NAME 问题 ----
print("\n--- [6] 检查 SCRIPT_NAME ---")
# 从 testenv CGI 输出中提取 SCRIPT_NAME
out, _ = run('curl -s http://127.0.0.1/d/testenv 2>&1 | grep SCRIPT_NAME', "SCRIPT_NAME")

# ---- 7. 检查 auth 二进制中 getenv 调用 ----
print("\n--- [7] 检查 auth 二进制 getenv 调用 ---")
run('strings /Server/www/d/auth | grep -i "SCRIPT_NAME\\|REMOTE_ADDR\\|QUERY_STRING\\|HTTP_COOKIE" | head -10', "auth 中的环境变量名")

# ---- 8. 清理测试 CGI ----
print("\n--- [8] 清理 ---")
run('rm -f /Server/www/d/testenv', "删除 testenv")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
