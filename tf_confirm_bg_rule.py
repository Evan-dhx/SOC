import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("确认 login-page 背景规则", r"""
cd /Server/www/ui
python3 - <<'PYEOF'
import re
src = open('index.html').read()
m = re.search(r'\.login-page \{', src)
print('login-page 规则起始:', m.start() if m else '未找到')
if m:
    print(src[m.start():m.start()+200])
m2 = re.search(r'body, #root \{', src)
print('body 规则:', m2.group(0) if m2 else '未找到')
PYEOF
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