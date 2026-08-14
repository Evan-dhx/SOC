import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=30):
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:8000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("检查版本号渲染问题")
print("=" * 70)

# ---- 1. 检查 config.js 完整内容 ----
print("\n--- [1] config.js 完整内容 ---")
run('cat /Server/www/ui/app-config/config.js', "config.js")

# ---- 2. 检查 config.js 修改时间 ----
print("\n--- [2] config.js 文件信息 ---")
run('ls -la /Server/www/ui/app-config/config.js', "文件信息")
run('md5sum /Server/www/ui/app-config/config.js', "MD5")

# ---- 3. 检查 config.js.bak ----
print("\n--- [3] config.js.bak 备份 ---")
run('cat /Server/www/ui/app-config/config.js.bak 2>/dev/null || echo "无备份"', "config.js.bak")

# ---- 4. 检查 index.html 中如何加载 config.js ----
print("\n--- [4] index.html 中 config.js 加载方式 ---")
run('grep -n "config\\|app-config\\|appConfig" /Server/www/ui/index.html', "config.js 引用")

# ---- 5. 检查是否有其他 config.js 文件 ----
print("\n--- [5] 搜索其他 config.js ---")
run('find /Server/www/ui -name "config.js" -type f 2>/dev/null', "所有 config.js")

# ---- 6. 检查 Apache 缓存配置 ----
print("\n--- [6] Apache 缓存配置 ---")
run('grep -r "Cache\\|cache\\|expires\\|Expires" /etc/httpd/conf.d/ly_server.conf 2>/dev/null || echo "无缓存配置"', "缓存配置")

# ---- 7. 通过 curl 检查 config.js 实际返回内容 ----
print("\n--- [7] curl 获取 config.js ---")
run('curl -s http://127.0.0.1/app-config/config.js 2>&1', "curl config.js")
run('curl -s -I http://127.0.0.1/app-config/config.js 2>&1', "curl headers")

# ---- 8. 检查 main.js 中版本号渲染代码 ----
print("\n--- [8] main.js 中版本号渲染 ---")
run('grep -o "version-text[^}]*}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "version-text 渲染")
run('grep -o "appConfig[^,]*" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "appConfig 引用")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
