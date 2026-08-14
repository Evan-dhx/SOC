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
print("查找左侧 SHADOW 残留 + 版本号修改")
print("=" * 70)

# ---- 1. 搜索 main.js 中的 SHADOW ----
print("\n--- [1] main.js 中的 SHADOW ---")
run('grep -o ".\\{0,50\\}SHADOW.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "SHADOW 上下文")

# ---- 2. 搜索 main.js 中的 FLOW 上下文（更详细）----
print("\n--- [2] main.js 中的 FLOW 上下文 ---")
run('grep -o ".\\{0,80\\}FLOW.\\{0,80\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "FLOW 上下文（详细）")

# ---- 3. 搜索 config.js 中的版本号 ----
print("\n--- [3] config.js 版本号 ---")
run('cat /Server/www/ui/app-config/config.js 2>/dev/null', "当前 config.js")

# ---- 4. 搜索 main.js 中版本号相关代码 ----
print("\n--- [4] main.js 中版本号代码 ---")
run('grep -o ".\\{0,50\\}subName.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "subName 上下文")
run('grep -o ".\\{0,50\\}version.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "version 上下文")
run('grep -o ".\\{0,50\\}appConfig.\\{0,50\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "appConfig 上下文")

# ---- 5. 搜索登录按钮相关代码 ----
print("\n--- [5] 登录按钮相关代码 ---")
run('grep -o ".\\{0,60\\}登录.\\{0,60\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "登录按钮上下文")
# 搜索 Unicode 编码的"登录"
run('grep -o ".\\{0,40\\}\\\\u767b\\\\u5f55.\\{0,40\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "登录 Unicode 上下文")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
