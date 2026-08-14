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
print("查看 process 函数完整逻辑")
print("=" * 70)

# process 函数
print("\n--- [1] process 函数 (310-380行) ---")
run('sed -n "310,380p" /root/SOC/ly_server_src/server/auth.cpp', "process 前段")

print("\n--- [2] process 函数 (380-450行) ---")
run('sed -n "380,450p" /root/SOC/ly_server_src/server/auth.cpp', "process 中段")

print("\n--- [3] process 函数 (450-530行) ---")
run('sed -n "450,530p" /root/SOC/ly_server_src/server/auth.cpp', "process 后段")

print("\n--- [4] main 函数整体 ---")
run('sed -n "/^int main/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp | head -40', "main 函数")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)