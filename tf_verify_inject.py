import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("结构验证", r"""
echo "=== 1. index.html 关键节点位置 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
print("head style 注入:", "ly-tech-login-style" in src)
print("body script 注入:", "ly-net-anim" in src)
print("chunk js 引用:", "main.ff156c89.chunk.js" in src, "2.2db6edf7.chunk.js" in src)
print("runtime 引用:", "webpackJsonp" in src)
print("文件大小:", len(src))
# 检查顺序：style 应在 head，script 应在 body 末尾
i_style = src.find('ly-tech-login-style')
i_script = src.find('ly-net-anim')
i_head = src.find('</head>')
i_body = src.find('</body>')
print(f"style位置={i_style} head结束={i_head} script位置={i_script} body结束={i_body}")
print("顺序OK:", i_style < i_head < i_script < i_body)
PYEOF
echo ""
echo "=== 2. 页面完整响应（前 600 字符） ==="
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | head -c 600
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