import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Find TF protobuf libraries
print('=== Finding TF protobuf libs ===')
i, o, e = c.exec_command("find /root/.cache/bazel -name 'libprotobuf.so*' -type f 2>/dev/null | head -10", timeout=30)
print(o.read().decode().strip())

print()
print('=== Finding TF protoc binaries ===')
i, o, e = c.exec_command("find /root/.cache/bazel -name 'protoc' -type f 2>/dev/null | head -5", timeout=30)
print(o.read().decode().strip())

# Also check /usr/local/lib for what's there
print()
print('=== Check /usr/local/lib protobuf ===')
i, o, e = c.exec_command("ls -la /usr/local/lib/libprotobuf* 2>/dev/null | head -10", timeout=10)
print(o.read().decode().strip())

c.close()