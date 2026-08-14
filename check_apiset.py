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
print("检查 api_set 和关键细节")
print("=" * 70)

# ---- api_set 定义 ----
print("\n--- [1] api_set 定义 ---")
run('grep -n "api_set" /root/SOC/ly_server_src/server/auth.cpp | head -10', "api_set")
run('sed -n "/api_set/,/};/p" /root/SOC/ly_server_src/server/auth.cpp | head -20', "api_set 内容")

# ---- process 函数完整逻辑 ----
print("\n--- [2] process 函数完整代码 ---")
run('sed -n "/^static int process/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp', "process 完整")

# ---- get_uid 函数 ----
print("\n--- [3] get_uid 函数 ---")
run('sed -n "/get_uid/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp | head -20', "get_uid")

# ---- check_session 完整逻辑 ----
print("\n--- [4] check_session 完整 ---")
run('sed -n "/check_session/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp | head -30', "check_session")

# ---- auth.cpp 完整行数 ----
print("\n--- [5] auth.cpp 结构 ---")
run('wc -l /root/SOC/ly_server_src/server/auth.cpp', "行数")
run('grep -n "^static\\|^int main\\|^}" /root/SOC/ly_server_src/server/auth.cpp', "函数结构")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)