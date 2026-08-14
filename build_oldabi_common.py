import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Build old-ABI static common library
print("=== Building old-ABI static common ===")
cmd = r"""
# Create old-ABI common build directory
rm -rf /root/SOC/ly_analyser_src/common_oldabi
mkdir -p /root/SOC/ly_analyser_src/common_oldabi
cd /root/SOC/ly_analyser_src/common_oldabi

# Copy source files needed
cp /root/SOC/ly_analyser_src/common/Makefile .
cp /root/SOC/ly_analyser_src/common/*.cpp .
cp /root/SOC/ly_analyser_src/common/*.h .
cp /root/SOC/ly_analyser_src/common/*.proto .

# Modify Makefile for old ABI, static only
sed -i 's/CXXFLAGS=-Wall -g -fPIC -std=c++1y -O2/CXXFLAGS=-Wall -g -std=c++1y -O2 -D_GLIBCXX_USE_CXX11_ABI=0/' Makefile
# Remove shared lib targets and LDFLAGS
sed -i 's/LDFLAGS=.*/#removed/' Makefile
sed -i 's/-shared//' Makefile

# Build only object files and static lib
make clean 2>&1 | tail -1

# Compile all source files
SRCS=$(ls *.cpp | grep -v baseline)
for f in $SRCS; do
  g++ -c -Wall -g -std=c++1y -O2 -D_GLIBCXX_USE_CXX11_ABI=0 -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/usr/local/include $f -o $(basename $f .cpp).o 2>&1 | grep -i error || true
done

# Generate protobuf files
for p in *.proto; do
  protoc $p --cpp_out=. 2>/dev/null
  pb_cc=$(basename $p .proto).pb.cc
  if [ -f "$pb_cc" ]; then
    g++ -c -Wall -g -std=c++1y -O2 -D_GLIBCXX_USE_CXX11_ABI=0 -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/usr/local/include $pb_cc -o $(basename $pb_cc .cc).o 2>&1 | grep -i error || true
  fi
done

# Create static library
OBJS=$(ls *.o 2>/dev/null)
ar rcs libcommon_oldabi.a $OBJS
echo "Created libcommon_oldabi.a"
ls -la libcommon_oldabi.a

# Check symbols
nm libcommon_oldabi.a 2>/dev/null | grep 'ipnum_to_ipstr' | head -5
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
