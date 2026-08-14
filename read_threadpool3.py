import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Read lines 24-40 of threadpool.hpp
print("=== Reading threadpool.hpp lines 24-40 ===")
cmd = r"""sed -n '24,40p' /root/SOC/ly_server_src/common/threadpool.hpp | cat -n"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Also check the ly_analyser version
print("\n=== ly_analyser threadpool.hpp lines 24-40 ===")
cmd2 = r"""sed -n '24,40p' /root/SOC/ly_analyser_src/common/threadpool.hpp | cat -n"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
