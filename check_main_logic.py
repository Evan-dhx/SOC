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
print("查看 main 函数核心逻辑")
print("=" * 70)

# ---- 查看 auth.cpp 主处理逻辑 ----
print("\n--- [1] 第 280-360 行（login/config 处理） ---")
run('sed -n "280,360p" /root/SOC/ly_server_src/server/auth.cpp', "280-360行")

# ---- 其他请求处理 ----
print("\n--- [2] 第 490-540 行（其他请求处理） ---")
run('sed -n "490,540p" /root/SOC/ly_server_src/server/auth.cpp', "490-540行")

# ---- do_auth_status 完整代码 ----
print("\n--- [3] do_auth_status 函数 - after create_session ---")
run('sed -n "/do_auth_status/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp | head -60', "do_auth_status 完整")

# ---- main 函数头部 ----
print("\n--- [4] main 函数前 50 行 ---")
run('sed -n "/int main/,/do_login/p" /root/SOC/ly_server_src/server/auth.cpp | head -60', "main 函数开头")

# ---- 非 login/config 请求如何处理 ----
print("\n--- [5] main 函数其他处理分支 ---")
run('sed -n "380,490p" /root/SOC/ly_server_src/server/auth.cpp', "380-490行")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)