import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("modified_bak 差异分析", r"""
echo "=== 1. modified_bak 中'未登录'相关 ==="
grep -o "未登录[^\"']\{0,30\}" /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak 2>/dev/null | head -5
echo ""
echo "=== 2. 修改版 vs 原版：首次差异位置 ==="
cmp /Server/www/ui/static/js/main.ff156c89.chunk.js /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak 2>&1 | head -3
echo ""
echo "=== 3. 修改版 vs 原版：差异片段（前 3 处） ==="
python3 - <<'PYEOF'
orig = open('/Server/www/ui/static/js/main.ff156c89.chunk.js').read()
mod = open('/Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak').read()
# 找第一个差异点
import difflib
sm = difflib.SequenceMatcher(None, orig, mod)
count = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != 'equal' and count < 4:
        print(f"--- {tag} (orig {i1}:{i2}, mod {j1}:{j2}) ---")
        print("原版: " + orig[i1:i1+120])
        print("修改: " + mod[j1:j1+120])
        print()
        count += 1
PYEOF
echo ""
echo "=== 4. 修改版中登录相关逻辑 ==="
grep -o "auth_pass[^,}]\{0,60\}" /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak 2>/dev/null | head -5
grep -o "登录成功[^\"']\{0,20\}" /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak 2>/dev/null | head -3
echo ""
echo "=== 5. 当前原版中登录相关 ==="
grep -o "auth_pass[^,}]\{0,60\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5
grep -o "登录成功[^\"']\{0,20\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()