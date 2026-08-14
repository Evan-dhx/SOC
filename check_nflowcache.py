import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the error context
print("=== nflowcache.c around line 950 ===")
cmd = "sed -n '945,975p' /root/SOC/ly_analyser_src/nfdump/bin/nflowcache.c"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Check CFLAGS for -Werror
print("\n=== Check for -Werror ===")
cmd2 = "grep -n 'Werror\\|Wpointer-arith' /root/SOC/ly_analyser_src/nfdump/bin/Makefile | head -5"
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode())

# Check full compile error
print("\n=== Full compile error ===")
cmd3 = "cd /root/SOC/ly_analyser_src/nfdump/bin && make nfdump-nflowcache.o 2>&1 | head -30"
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
