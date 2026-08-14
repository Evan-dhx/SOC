import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Strategy: Compile TF-dependent files with old ABI, rest with new ABI
# Then create a combined flow_filter_mixed.a

print("=== Step 1: Recompile TF files with old ABI ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/flow
mkdir -p /tmp/flow_oldabi

# Compile TF-dependent files with old ABI
TF_FILES="dga_filter.cpp dnstun_ai_filter.cpp mining_filter.cpp threat_filter.cpp"
TF_INCS="-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf/ -I/usr/local/include/tf/bazel-genfiles -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/tensorflow/third-party -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto"

for f in $TF_FILES; do
  echo "Compiling $f with old ABI..."
  g++ -c -Wall -fPIC -g -std=c++11 -D_GLIBCXX_USE_CXX11_ABI=0 -DAGENT -O2 -I../../common $TF_INCS $f -o /tmp/flow_oldabi/$(basename $f .cpp).o 2>&1
done

echo "Old ABI objects:"
ls -la /tmp/flow_oldabi/
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
print(stdout.read().decode())
print(stderr.read().decode())

# Step 2: Create mixed flow_filter.a
print("\n=== Step 2: Create mixed flow_filter ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Extract new-ABI objects from flow_filter.a
rm -rf /tmp/flow_mixed && mkdir -p /tmp/flow_mixed
cd /tmp/flow_mixed
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter.a

# Replace TF-dependent objects with old-ABI versions
cp /tmp/flow_oldabi/dga_filter.o .
cp /tmp/flow_oldabi/dnstun_ai_filter.o .
cp /tmp/flow_oldabi/mining_filter.o .
cp /tmp/flow_oldabi/threat_filter.o .

# Create mixed archive
ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_mixed.a *.o
echo "Created flow_filter_mixed.a"
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter_mixed.a
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Step 3: Update indexing to use mixed library
print("\n=== Step 3: Update indexing and rebuild ===")
cmd3 = r"""
cd /root/SOC/ly_analyser_src/agent/indexing
sed -i 's|flow_filter.a|flow_filter_mixed.a|' Makefile
# Also add -lstdc++fs if needed
make clean 2>&1 | tail -1
make 2>&1 | tail -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
