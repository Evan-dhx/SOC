import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("完整重编 libcommon（清 .o）", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. 清理全部 .o 与库 ==="
rm -f *.o libcommon.a libcommon.so
rm -f /tmp/common_err.log
echo ""
echo "=== 2. 编译全部 .cpp ==="
SRCS="ly_strings.cpp log.cpp ip.cpp datetime.cpp topn_req.cpp sha256.cpp http.cpp file.cpp ini.cpp config.cpp mo_req.cpp md5.cpp cJSON.cpp slice.cpp stringutil.cpp scoped_mmap.cpp mmapped_file.cpp event_req.cpp feature_req.cpp topn_param.cpp CMyINI.cpp asset.cpp ctl_req.cpp event_feature_req.cpp tic.cpp evidence_req.cpp"
FAIL=0
for f in $SRCS; do
  g++ -c -Wall -g -fPIC -std=c++17 -O2 -I. -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o ${f%.cpp}.o $f 2>>/tmp/common_err.log || { echo "FAIL $f"; FAIL=1; }
done
echo "cpp 完成 FAIL=$FAIL"
echo ""
echo "=== 3. 编译全部 .pb.cc ==="
for f in *.pb.cc; do
  g++ -c -Wall -g -fPIC -std=c++17 -O2 -I. -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o ${f%.cc}.o $f 2>>/tmp/common_err.log || { echo "FAIL $f"; FAIL=1; }
done
echo "pb 完成 FAIL=$FAIL"
echo ""
echo "=== 4. 打包 ==="
ar rcs libcommon.a *.o
echo "libcommon.a: $(ar t libcommon.a | wc -l) objects"
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lprotobuf -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -3
ls -la libcommon.a libcommon.so
cp libcommon.so /lib64/ && cp libcommon.so /usr/lib64/ && ldconfig
echo ""
echo "=== 5. 错误检查 ==="
grep -c "error" /tmp/common_err.log 2>/dev/null || echo 0
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()