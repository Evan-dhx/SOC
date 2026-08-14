import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check TensorFlow library symbols
print("=== Checking TF symbols ===")
cmd = r"""nm -D /usr/local/lib/libtensorflow_cc.so 2>/dev/null | grep 'Status.*ToString' | head -10"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check with cxx11 ABI tag
print("\n=== Checking TF cxx11 symbols ===")
cmd2 = r"""nm -D /usr/local/lib/libtensorflow_cc.so 2>/dev/null | grep 'cxx11' | head -10"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check ReadBinaryProto
print("\n=== Checking ReadBinaryProto ===")
cmd3 = r"""nm -D /usr/local/lib/libtensorflow_cc.so 2>/dev/null | grep 'ReadBinaryProto' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check CheckOpMessageBuilder
print("\n=== Checking CheckOpMessageBuilder ===")
cmd4 = r"""nm -D /usr/local/lib/libtensorflow_cc.so 2>/dev/null | grep 'CheckOpMessageBuilder' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
