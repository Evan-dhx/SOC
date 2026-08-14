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
print("查看品牌名称出现的具体上下文")
print("=" * 70)

# ---- 1. 查看 main.js 中 "Flow Shadow" 上下文 ----
print("\n--- [1] main.js 中 'Flow Shadow' 上下文 ---")
run('grep -io ".\\{0,60\\}flow.shadow.\\{0,60\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "Flow Shadow 上下文")

# ---- 2. 查看 main.js 中 "shadowflow" 上下文 ----
print("\n--- [2] main.js 中 'shadowflow' 上下文 ---")
run('grep -o ".\\{0,40\\}shadowflow.\\{0,40\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "shadowflow 上下文")

# ---- 3. 查看 index.html 中 "shadowflow" 上下文 ----
print("\n--- [3] index.html 中 'shadowflow' 上下文 ---")
run('grep -o ".\\{0,40\\}shadowflow.\\{0,40\\}" /Server/www/ui/index.html 2>/dev/null', "shadowflow 上下文")

# ---- 4. 查看 runtime-main.js 中 "shadowflow" 上下文 ----
print("\n--- [4] runtime-main.js 中 'shadowflow' 上下文 ---")
run('grep -o ".\\{0,40\\}shadowflow.\\{0,40\\}" /Server/www/ui/static/js/runtime-main.70783980.js 2>/dev/null', "shadowflow 上下文")

# ---- 5. 查看 2.2db6edf7.chunk.js 中 "shadowflow" 上下文 ----
print("\n--- [5] 2.chunk.js 中 'shadowflow' 上下文 ---")
run('grep -o ".\\{0,40\\}shadowflow.\\{0,40\\}" /Server/www/ui/static/js/2.2db6edf7.chunk.js 2>/dev/null | head -5', "shadowflow 上下文")

# ---- 6. 搜索 main.js 中是否有中文品牌文本 ----
print("\n--- [6] main.js 中文品牌相关文本 ---")
run('grep -o ".\\{0,30\\}流影.\\{0,30\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "main.js 流影上下文")
# 可能"流影"编码为 Unicode
run('grep -o ".\\{0,30\\}\\\\u6d41\\\\u5f7.\\{0,30\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "main.js Unicode 流影")
run('grep -o ".\\{0,30\\}\\\\u6d41\\\\u5f71.\\{0,30\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10', "main.js Unicode 流影 v2")

# ---- 7. 搜索 robots.txt ----
print("\n--- [7] robots.txt ---")
run('cat /Server/www/ui/robots.txt 2>/dev/null', "robots.txt")

# ---- 8. 搜索 template 目录 ----
print("\n--- [8] template 目录 ---")
run('ls -la /Server/www/ui/template/ 2>/dev/null', "template 目录")
run('grep -rn "流影\\|flow.shadow\\|shadowflow" /Server/www/ui/template/ 2>/dev/null', "template 中的品牌")

# ---- 9. 搜索 asset-config 目录 ----
print("\n--- [9] asset-config 目录 ---")
run('ls -la /Server/www/ui/asset-config/ 2>/dev/null', "asset-config 目录")
run('grep -rn "流影\\|flow.shadow\\|shadowflow" /Server/www/ui/asset-config/ 2>/dev/null', "asset-config 中的品牌")

# ---- 10. 搜索 theme 目录 ----
print("\n--- [10] theme 目录 ---")
run('ls -la /Server/www/ui/theme/ 2>/dev/null', "theme 目录")
run('grep -rn "流影\\|flow.shadow\\|shadowflow" /Server/www/ui/theme/ 2>/dev/null', "theme 中的品牌")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
