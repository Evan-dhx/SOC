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
        print(out.strip()[:15000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("搜索版本号渲染代码 + 执行全部修改")
print("=" * 70)

# ---- 1. 搜索版本号标签渲染代码 ----
print("\n--- [1] 版本号标签渲染代码 ---")
# 搜索 subName 和 version 的使用
run('grep -o ".\\{0,100\\}Wa.\\{0,100\\}Ga.\\{0,100\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "Wa/Ga (subName/version) 使用")
# 搜索 version-text class
run('grep -o ".\\{0,100\\}version-text.\\{0,100\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "version-text class")
# 搜索 version 标签渲染
run('grep -o ".\\{0,80\\}version.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | grep -v "svg\\|1.1\\|viewBox" | head -10', "version 标签（排除svg）")

# ---- 2. 搜索登录按钮和版本号在DOM中的位置 ----
print("\n--- [2] 登录页面 DOM 结构 ---")
# 搜索 login-right 或 login-form 相关的 DOM 结构
run('grep -o ".\\{0,200\\}login-right.\\{0,200\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3', "login-right 上下文")
run('grep -o ".\\{0,200\\}login-form.\\{0,200\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3', "login-form 上下文")
# 搜索登录按钮
run('grep -o ".\\{0,200\\}login-btn.\\{0,200\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3', "login-btn 上下文")
run('grep -o ".\\{0,200\\}login-button.\\{0,200\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3', "login-button 上下文")

# ---- 3. 搜索 subName 在登录页面中的使用 ----
print("\n--- [3] subName 在登录页面中的使用 ---")
run('grep -o ".\\{0,150\\}gj.\\{0,150\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "gj (subName) 使用")
run('grep -o ".\\{0,150\\}yj.\\{0,150\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "yj (version) 使用")

# ---- 4. 搜索完整的登录页面组件 ----
print("\n--- [4] 登录页面组件 ---")
# 搜索包含 login-title 或 version-text 的代码块
run('grep -o ".\\{0,300\\}version-text.\\{0,300\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null', "version-text 上下文（详细）")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
