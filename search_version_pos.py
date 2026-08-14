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
        print(out.strip()[:10000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("搜索版本号渲染位置")
print("=" * 70)

# 用 python3 脚本文件搜索，避免引号问题
search_script = """
import re
with open('/Server/www/ui/static/js/main.ff156c89.chunk.js', 'r') as f:
    s = f.read()

# 搜索 version-text
for m in re.finditer(r'.{0,300}version-text.{0,300}', s):
    print('=== version-text ===')
    print(m.group()[:600])
    print()

# 搜索 subName 使用
for m in re.finditer(r'subName', s):
    ctx = s[max(0,m.start()-100):m.end()+200]
    print('=== subName ===')
    print(ctx[:300])
    print()

# 搜索 version 的使用（排除 svg version="1.1"）
for m in re.finditer(r'version(?!_text|"1\.1")', s):
    ctx = s[max(0,m.start()-100):m.end()+200]
    if 'svg' not in ctx and 'viewBox' not in ctx:
        print('=== version ===')
        print(ctx[:300])
        print()

# 搜索 login-btn
for m in re.finditer(r'login-btn', s):
    ctx = s[max(0,m.start()-200):m.end()+200]
    print('=== login-btn ===')
    print(ctx[:400])
    print()

# 搜索 login-button
for m in re.finditer(r'login-button', s):
    ctx = s[max(0,m.start()-200):m.end()+200]
    print('=== login-button ===')
    print(ctx[:400])
    print()
"""

# 将搜索脚本写到远程文件
sftp = c.open_sftp()
with sftp.file('/tmp/search_version.py', 'w') as f:
    f.write(search_script)
sftp.close()

run('python3 /tmp/search_version.py 2>&1', "版本号渲染位置搜索", timeout=30)

c.close()
print("\n搜索完成!")
