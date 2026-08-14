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
    if out.strip(): print(out.strip()[:8000])
    if err.strip(): print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("检查 main.js 替换前后差异")
print("=" * 70)

# ---- 1. 检查 bak 是否存在 ----
print("\n--- [1] 检查备份文件 ---")
run('ls -la /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null', "main.js.bak")
run('ls -la /Server/www/ui/static/js/main.ff156c89.chunk.js', "main.js 当前")

# ---- 2. 对比替换前后的差异 ----
print("\n--- [2] 检查替换内容 ---")
# 搜索替换后的字符串
run('grep -c "NETWORK TRAFFIC SITUATIONAL AWARENESS PLATFORM" /Server/www/ui/static/js/main.ff156c89.chunk.js', "长文本出现次数")
run('grep -c "NETWORK TRAFFIC" /Server/www/ui/static/js/main.ff156c89.chunk.js', "NETWORK TRAFFIC 出现次数")
run('grep -c "SITUATIONAL AWARENESS" /Server/www/ui/static/js/main.ff156c89.chunk.js', "SITUATIONAL AWARENESS 出现次数")

# ---- 3. 查看 bak 中原始 FLOW SHADOW 出现次数 ----
if False:
    pass  # bak may not exist

run('grep -c "FLOW SHADOW" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null', "bak 中 FLOW SHADOW")
run('grep -c "FLOW" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null', "bak 中 FLOW")
run('grep -c "SHADOW" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null', "bak 中 SHADOW")

# ---- 4. 查看 main.js 中 NETWORK TRAFFIC 的上下文 ----
print("\n--- [4] NETWORK TRAFFIC 在 main.js 中的上下文 ---")
run('grep -oP ".{0,80}NETWORK TRAFFIC.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "NETWORK TRAFFIC 上下文")

# ---- 5. 检查 bak 中 FLOW 的上下文（看是否在原位置） ----
print("\n--- [5] bak 中 FLOW SHADOW 的上下文 ---")
if True:
    run('grep -oP ".{0,80}FLOW SHADOW.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null | head -10', "bak 中 FLOW SHADOW 上下文")
    run('grep -oP ".{0,80}\"FLOW\".{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null | head -10', "bak 中 \"FLOW\" 上下文")
    run('grep -oP ".{0,80}\"SHADOW\".{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js.bak 2>/dev/null | head -10', "bak 中 \"SHADOW\" 上下文")

# ---- 6. 检查是否还有其他地方也被错误替换 ----
print("\n--- [6] 检查是否有异常替换 ---")
run('grep -oP ".{0,100}SHADOW.{0,100}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 main.js 中 SHADOW 残留")
run('grep -oP ".{0,80}NETWORK.{0,80}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "当前 main.js 中 NETWORK")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)