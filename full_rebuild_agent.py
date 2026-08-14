import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix indexing Makefile link order - add --start-group/--end-group
print("=== Fixing indexing link order with group ===")
cmd = r"""cd /root/SOC/ly_analyser_src/agent/indexing && cat Makefile | grep 'indexer:' | tail -1"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print("Current link line:", stdout.read().decode())

# Replace the link rule to use --start-group/--end-group for circular deps
cmd2 = r"""cd /root/SOC/ly_analyser_src/agent/indexing
# Update the linker rule
sed -i '/^indexer:/{n;s|.*|\t$(CXX) $(CXXFLAGS) $(INCS) -o $@ indexer.o flow_indexer.o cache_generator.o $(LDFLAGS) -Wl,--start-group $(LIBS) $(LDLIBS) -Wl,--end-group|}' Makefile
echo 'Updated link rule'
grep -A1 'indexer:' Makefile | tail -2"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild all agent modules from scratch
print("\n=== Full agent rebuild ===")
cmd3 = r"""
cd /root/SOC/ly_analyser_src/agent
# Rebuild each module in order
for dir in dump config model data flow; do
  echo "=== Building $dir ==="
  cd /root/SOC/ly_analyser_src/agent/$dir
  make clean 2>&1 | tail -1
  if [ "$dir" = "flow" ]; then
    make flow_filter.a 2>&1 | tail -3
  else
    make -j4 2>&1 | tail -3
  fi
done

echo "=== Building indexing ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean 2>&1 | tail -1
make 2>&1 | tail -30
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=600)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
