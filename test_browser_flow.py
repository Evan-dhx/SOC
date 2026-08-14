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
print("模拟浏览器精确请求序列并检查 cookie")
print("=" * 70)

# 上传精确模拟脚本
sftp = c.open_sftp()
with sftp.file('/tmp/test_browser_flow.py', 'w') as f:
    f.write("""import urllib.request, http.cookiejar, sys
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Pre-login config (like browser does on page load)
print("=== Step 1: Pre-login config request ===")
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, 
    headers={"Content-Type": "application/x-www-form-urlencoded"})
try:
    resp = opener.open(req)
    print("Body:", resp.read().decode()[:200])
    print("Status:", resp.status)
except Exception as e:
    print("Error:", e)
print("Cookies:", [(c.name, c.value, c.domain, c.path) for c in cj])

# Step 2: Login
print()
print("=== Step 2: Login ===")
data = b"auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3"
req = urllib.request.Request("http://127.0.0.1/d/login", data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded", 
             "Accept": "application/json, text/plain, */*"})
resp = opener.open(req)
print("Body:", resp.read().decode()[:200])
print("Status:", resp.status)
print("Cookies:", [(c.name, c.value, c.domain, c.path) for c in cj])

# Step 3: Config after login
print()
print("=== Step 3: Config after login ===")
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
print("Body:", resp.read().decode()[:500])
print("Status:", resp.status)
print("Cookies:", [(c.name, c.value, c.domain, c.path) for c in cj])

# Step 4: User config
print()
print("=== Step 4: User config after login ===")
data = b"auth_target=config&type=user&op=GET"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
body = resp.read().decode()
print("Body:", body[:500])
print("Status:", resp.status)

# Show all cookies at end
print()
print("=== Final Cookies ===")
for c in cj:
    print(f"  {c.name}={c.value} domain={c.domain} path={c.path} expires={c.expires}")
""")
sftp.close()

run('python3 /tmp/test_browser_flow.py 2>&1', "浏览器精确模拟")

print()
print("=" * 70)
print("现在检查 auth.cpp 中 Set-Cookie 的 Version=1 问题")
print("=" * 70)

# 检查 Cgicc 库中 HTTPCookie 的实现
run('grep -rn "Version\\|setMaxAge\\|setCookie" /usr/include/cgicc/HTTPCookie.h 2>/dev/null | head -20', "HTTPCookie.h")
run('grep -rn "Version" /usr/include/cgicc/ 2>/dev/null | head -10', "cgicc Version")

# 检查编译后的 auth binary 是否有 Version=1 硬编码
run('strings /Server/www/d/auth | grep -i "Version.*1\\|SESSION_ID" | head -10', "binary strings")

c.close()
print("检查完成!")