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
print("检查 mod_headers 和修复 Header edit")
print("=" * 70)

# ---- 检查 mod_headers ----
print("\n--- [1] 检查 mod_headers ---")
run('httpd -M 2>/dev/null | grep -i headers', "mod_headers 状态")

# ---- 查看当前的 ly_server.conf ----
print("\n--- [2] 查看 ly_server.conf ---")
run('cat /etc/httpd/conf.d/ly_server.conf', "ly_server.conf")

# ---- 检查 httpd 错误日志 ----
print("\n--- [3] httpd 错误日志 ---")
run('tail -10 /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)