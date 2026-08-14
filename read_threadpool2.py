import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read the full threadpool.hpp with line numbers
print("=== Reading threadpool.hpp with line numbers ===")
cmd = r"""cat -n /root/SOC/ly_server_src/common/threadpool.hpp"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
