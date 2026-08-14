import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 清理残留进程（install.sh 及其子进程）
def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out + (f"\nSTDERR: {err[:500]}" if err else "")

print("=== 清理残留进程 ===")
print(run("kill -9 486618 486623 2>/dev/null; sleep 1; ss -tlnp 2>/dev/null | grep -c 8090"))

# 2. 重传修复后的 server.py
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ti_server\server.py', '/opt/ti_server/server.py')
sftp.close()
print("server.py 已更新")

# 3. 重新部署
print(run("cd /opt/ti_server && ./install.sh 8090", timeout=180))

client.close()