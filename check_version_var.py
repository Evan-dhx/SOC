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
print("检查版本号变量来源与 HTTP 客户端关系")
print("=" * 70)

# ---- 1. 检查 bak main.js 中 gj 和 yj 的定义 ----
print("\n--- [1] bak main.js 中 gj 和 yj 定义 ---")
# 搜索 gj 定义（可能是 var gj= 或 let gj= 或 gj=）
run('grep -oP "gj\\s*=\\s*[^;]+" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "gj 定义")
run('grep -oP "yj\\s*=\\s*[^;]+" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "yj 定义")

# 搜索更宽松的模式
run('grep -oP "[,\\s(]gj[,\\s=)\\]]" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -20', "gj 出现")
run('grep -oP ".{0,30}gj.{0,30}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | grep -i "appConfig\\|config\\|subName\\|version" | head -10', "gj 与 config 关联")

# ---- 2. 搜索 appConfig.subName 和 appConfig.version ----
print("\n--- [2] 搜索 appConfig.subName / version ---")
run('grep -oP ".{0,50}subName.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak subName")
run('grep -oP ".{0,50}subName.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 subName")

# ---- 3. 查看版本号渲染位置附近代码 ----
print("\n--- [3] version-text 附近代码 - bak ---")
run('grep -oP ".{0,200}version-text.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -5', "bak version-text 上下文")

# ---- 4. 查看 login-page 渲染代码 ----
print("\n--- [4] login-page 渲染代码 - 搜索完整的登录页组件 ---")
run('grep -oP ".{0,300}login_right.{0,300}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -5', "bak login_right")

# ---- 5. 检查 j 拦截器的配置 ----
print("\n--- [5] HTTP 客户端 j 的配置 ---")
run('grep -oP ".{0,100}j\\s*=\\s*.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak j 定义")

# ---- 6. 检查当前 main.js 中的相同内容 ----
print("\n--- [6] 当前 main.js HTTP 客户端 ---")
run('grep -oP ".{0,100}j\\s*=\\s*.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 j 定义")
run('grep -oP ".{0,100}interceptors.request.use.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "当前 request interceptor")

# ---- 7. 检查 yd （或类似的 HTTP 基础路径变量） ----
print("\n--- [7] 搜索 baseUrl 使用 ---")
run('grep -oP ".{0,60}baseUrl.{0,60}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak baseUrl")
run('grep -oP ".{0,60}baseUrl.{0,60}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 baseUrl")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)