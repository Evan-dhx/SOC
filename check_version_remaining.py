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
    if label: print(f"[{label}]")
    if out.strip(): print(out.strip()[:5000])
    if err.strip(): print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("检查所有'开源版 v1.0.2'相关位置")
print("=" * 70)

# ---- 1. config.js 当前状态 ----
print("\n--- [1] config.js 当前 ---")
run('cat /Server/www/ui/app-config/config.js', "config.js")

# ---- 2. config.js.bak ----
print("\n--- [2] config.js.bak ---")
run('cat /Server/www/ui/app-config/config.js.bak 2>/dev/null', "config.js.bak")

# ---- 3. bak 版本 main.js 中搜索版本号 ----
print("\n--- [3] bak main.js 中搜索版本号 ---")
run('grep -oP ".{0,50}version.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak version")
run('grep -oP ".{0,50}开源版.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak 开源版")
run('grep -oP ".{0,50}1\\.0\\.2.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak | head -10', "bak 1.0.2")

# ---- 4. 当前 main.js 中搜索版本号 ----
print("\n--- [4] 当前 main.js 中搜索版本号 ---")
run('grep -oP ".{0,50}version.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 version")
run('grep -oP ".{0,50}开源版.{0,50}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 开源版")

# ---- 5. 检查 index.html 是否有版本号 ----
print("\n--- [5] index.html 版本号 ---")
run('grep -i "version\\|v1\\.0\\|1\\.0\\.2\\|开源版" /Server/www/ui/index.html', "index.html 版本")

# ---- 6. 检查其他文件 ----
print("\n--- [6] 搜索所有文件 ---")
files = run('find /Server/www/ui -name "*.js" -o -name "*.html" -o -name "*.json" 2>/dev/null | head -30', "文件列表")
run('grep -l "开源版.*1\\.0\\.2\\|1\\.0\\.2.*开源版" /Server/www/ui/app-config/*.js /Server/www/ui/static/js/*.js /Server/www/ui/index.html 2>/dev/null', "开源版 v1.0.2")
run('grep -l "开源版" /Server/www/ui/app-config/*.js /Server/www/ui/static/js/*.js /Server/www/ui/index.html 2>/dev/null', "所有含开源版的文件")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)