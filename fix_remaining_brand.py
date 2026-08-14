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
        print(out.strip()[:10000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("修复残留 FLOW SHADOW + 解锁账号 + 检查登录请求")
print("=" * 70)

# ---- 1. 搜索所有文件中的 FLOW SHADOW（不区分大小写）----
print("\n--- [1] 搜索所有残留 FLOW SHADOW ---")
run('grep -ril "flow.shadow" /Server/www/ui/ 2>/dev/null', "所有文件")
run('grep -rn "FLOW SHADOW" /Server/www/ui/static/css/ 2>/dev/null', "CSS 文件")
run('grep -rn "flow.shadow" /Server/www/ui/static/css/ 2>/dev/null', "CSS 文件（小写）")
run('grep -rn "FLOW SHADOW" /Server/www/ui/static/js/ 2>/dev/null', "JS 文件")

# ---- 2. 搜索 CSS content 属性中的品牌名 ----
print("\n--- [2] CSS content 属性 ---")
run('grep -n "content.*flow\\|content.*shadow\\|content.*FLOW\\|content.*SHADOW" /Server/www/ui/static/css/*.css 2>/dev/null', "CSS content")
run('grep -rn "content" /Server/www/ui/static/css/main.c025dfb1.chunk.css 2>/dev/null | head -20', "main CSS content 属性")

# ---- 3. 搜索 main.css 中的品牌相关样式 ----
print("\n--- [3] main.css 中的品牌 ---")
run('grep -in "flow\\|shadow\\|brand\\|logo\\|title" /Server/www/ui/static/css/main.c025dfb1.chunk.css 2>/dev/null | head -20', "main CSS 品牌相关")

# ---- 4. 搜索所有 CSS 文件 ----
print("\n--- [4] 所有 CSS 文件搜索 ---")
run('find /Server/www/ui -name "*.css" -exec grep -l "FLOW\\|flow\\|shadow" {} \\; 2>/dev/null', "包含品牌名的 CSS")

# ---- 5. 在 main.js 中搜索 FLOW（不带 SHADOW）----
print("\n--- [5] main.js 中的 FLOW（不带SHADOW）---")
run('grep -o ".\\{0,30\\}FLOW.\\{0,30\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "FLOW 上下文")

# ---- 6. 在 2.chunk.js 中搜索 FLOW SHADOW ----
print("\n--- [6] 2.chunk.js 中的 FLOW SHADOW ---")
run('grep -o ".\\{0,30\\}FLOW.\\{0,30\\}" /Server/www/ui/static/js/2.2db6edf7.chunk.js 2>/dev/null | head -10', "2.chunk.js 中的 FLOW")

# ---- 7. 搜索 LESS 文件（可能编译进了 CSS）----
print("\n--- [7] LESS/媒体文件搜索 ---")
run('find /Server/www/ui -name "*.less" 2>/dev/null', "LESS 文件")
run('find /Server/www/ui/static/media -type f 2>/dev/null | head -20', "媒体文件")

# ---- 8. 解锁 admin 账号 ----
print("\n--- [8] 解锁 admin 账号 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0;" server 2>/dev/null', "解锁全部用户")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT id,name,level,lockedtime FROM t_user;" server 2>/dev/null', "解锁后状态")

# ---- 9. 检查前端登录请求格式 ----
print("\n--- [9] 前端登录请求分析 ---")
# 前端可能直接发送到 /d/login 而不是 /d/auth
run('curl -s -v -X POST -d "auth_user=admin&auth_pass=admin" http://127.0.0.1/d/login 2>&1 | head -20', "POST /d/login")
run('curl -s -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1 | head -20', "POST /d/auth with auth_target")

# ---- 10. 清理 httpd 日志并测试 ----
print("\n--- [10] 清理日志并测试 ----")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
# 先测试 curl 登录
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "curl admin/admin")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
