import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find json-c headers
print("=== Finding json-c headers ===")
cmd = r"""find /usr/include -name 'json.h' 2>/dev/null | grep -i json"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check json-c package
print("\n=== json-c package info ===")
cmd2 = r"""rpm -ql json-c-devel 2>&1 | grep -E '\.h$|\.pc$' | head -20"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check pkg-config
print("\n=== pkg-config for json-c ===")
cmd3 = r"""pkg-config --cflags --libs json-c 2>&1"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
