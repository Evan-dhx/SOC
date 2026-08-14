import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix indexing Makefile - remove old ABI flag, fix link order
print("=== Fixing indexing/Makefile ===")
cmd = r"""cd /root/SOC/ly_analyser_src/agent/indexing && sed -i 's/-D_GLIBCXX_USE_CXX11_ABI=0 //' Makefile && echo 'Fixed ABI flag' && grep 'CXXFLAGS=' Makefile | head -3"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Fix link order: move LIBS after LDLIBS
print("\n=== Fixing link order ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/agent/indexing && sed -i 's|$(CXX) \$\^ -o \$@ $(INCS) $(CXXFLAGS) $(LDFLAGS) $(LDLIBS)|$(CXX) $(CXXFLAGS) $(INCS) -o $@ indexer.o flow_indexer.o cache_generator.o $(LDFLAGS) $(LIBS) $(LDLIBS)|' Makefile && echo 'Fixed link order' && grep 'indexer:' Makefile | tail -2"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Also fix flow module ABI flag
print("\n=== Fixing flow/Makefile ABI flag ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/agent/flow && sed -i 's/-D_GLIBCXX_USE_CXX11_ABI=0 //' Makefile && echo 'Fixed flow ABI flag'"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Also fix model, data, config, handlers ABI flags
print("\n=== Fixing other modules ABI flags ===")
cmd4 = r"""for dir in model data config handlers; do
  if [ -f /root/SOC/ly_analyser_src/agent/$dir/Makefile ]; then
    sed -i 's/-D_GLIBCXX_USE_CXX11_ABI=0 //' /root/SOC/ly_analyser_src/agent/$dir/Makefile
    echo "Fixed $dir"
  fi
done"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile flow first (since ABI changed)
print("\n=== Recompiling flow module ===")
cmd5 = r"""cd /root/SOC/ly_analyser_src/agent/flow && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -20"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out[-2000:] if len(out) > 2000 else out)
if err.strip():
    print("=== STDERR ===")
    print(err[-1000:] if len(err) > 1000 else err)

client.close()
