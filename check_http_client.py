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
    if label: print(f"[{label}]")
    if out.strip(): print(out.strip()[:8000])
    if err.strip(): print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("检查前端 HTTP 客户端配置")
print("=" * 70)

# ---- 1. 搜索 withCredentials / credentials ----
print("\n--- [1] 搜索 withCredentials / credentials ---")
run('grep -oP ".{0,80}withCredentials.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "withCredentials")
run('grep -oP ".{0,80}credentials.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "credentials")
run('grep -oP ".{0,80}withCredential.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "withCredential")

# ---- 2. 搜索 xhr / XMLHttpRequest ----
print("\n--- [2] 搜索 xhr / XMLHttpRequest ---")
run('grep -oP ".{0,80}XMLHttpRequest.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "XMLHttpRequest")

# ---- 3. 搜索 ajax / $.ajax ----
print("\n--- [3] 搜索 $.ajax / axios ---")
run('grep -oP ".{0,80}\\.ajax.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "ajax")
run('grep -oP ".{0,80}\\.axios.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "axios")
run('grep -oP ".{0,80}axios.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "axios all")

# ---- 4. 搜索 request 拦截器/封装 ----
print("\n--- [4] 搜索 request 拦截器 ---")
run('grep -oP ".{0,80}interceptor.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "interceptor")
run('grep -oP ".{0,80}request.use.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "request.use")
run('grep -oP ".{0,80}response.use.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "response.use")

# ---- 5. 搜索 cookie / Cookie jar 相关 ----
print("\n--- [5] 搜索 cookie jar ---")
run('grep -oP ".{0,80}cookie.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -20', "cookie all")

# ---- 6. 从 main.js 中提取完整的 HTTP 配置代码 ----
print("\n--- [6] 搜索 http 请求封装 - search for request method ---")
# Try to find where $.post or fetch is configured
run('grep -oP ".{0,100}\\.post\\(.{0,100}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "post")
run('grep -oP ".{0,100}http.{0,100}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "http all")

# ---- 7. 检查 main.js 中是否有拦截器代码块 ----
print("\n--- [7] 搜索拦截器链 ---")
run('grep -oP ".{0,200}function[^{]*request[^{]*\\{.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "request function")

# ---- 8. 直接检查 2.2db6edf7.chunk.js (vendor) 中的 $.post ----
print("\n--- [8] vendor chunk 中的 $.post ---")
run('grep -oP ".{0,80}\\.post.{0,80}" /Server/www/ui/static/js/2.2db6edf7.chunk.js | head -10', "vendor $.post")

# ---- 9. 搜索 config.js 中是否有与 cookie 相关的配置 ----
print("\n--- [9] config.js cookie 相关 ---")
run('cat /Server/www/ui/app-config/config.js | grep -i "cookie\\|sid\\|session"', "config.js cookie")

# ---- 10. 检查 httpd 响应头中是否添加了任何影响 cookie 的 header ----
print("\n--- [10] httpd 全局配置 ---")
run('grep -r "Header\\|header" /etc/httpd/conf.d/ly_server.conf 2>/dev/null', "httpd header 配置")
run('grep -r "Cookie\\|cookie" /etc/httpd/conf.d/ 2>/dev/null', "httpd cookie 配置")
run('grep -r "SameSite\\|samesite" /etc/httpd/ 2>/dev/null', "SameSite 配置")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)