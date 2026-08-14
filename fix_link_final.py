import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check boost regex
print("=== Checking boost_regex ===")
cmd = r"""find /usr/lib64 /usr/lib -name 'libboost_regex*' 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Fix indexing Makefile - add missing libs
print("\n=== Fixing indexing LDLIBS ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/agent/indexing
sed -i 's|-lcommon -lboost_regex|-lcommon -lboost_regex -lcppdb -lcgicc -lcurl|' Makefile
echo 'Updated LDLIBS'
grep LDLIBS Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild indexing
print("\n=== Rebuilding indexing ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/agent/indexing && make clean 2>&1 | tail -1 && make 2>&1 | tail -20"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
