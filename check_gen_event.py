import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check how gen_event.cpp uses threadpool
print("=== gen_event.cpp threadpool usage ===")
cmd = r"""grep -n 'threadpool\|Threadpool\|commit\|pool' /root/SOC/ly_server_src/server/gen_event.cpp | head -30"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check the include
print("\n=== gen_event.cpp includes ===")
cmd2 = r"""head -20 /root/SOC/ly_server_src/server/gen_event.cpp"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check line 70 of Makefile where the error occurs
print("\n=== Makefile line 70 ===")
cmd3 = r"""sed -n '65,75p' /root/SOC/ly_server_src/server/Makefile"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
