import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("补编 7 个 _req.cpp + 重打包 libcommon", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. 补编（-fpermissive） ==="
SRCS="topn_req.cpp mo_req.cpp event_req.cpp feature_req.cpp ctl_req.cpp event_feature_req.cpp evidence_req.cpp"
FAIL=0
for f in $SRCS; do
  g++ -c -Wall -fpermissive -g -fPIC -std=c++17 -O2 -I. -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o ${f%.cpp}.o $f 2>>/tmp/common_err2.log || { echo "FAIL $f"; FAIL=1; }
done
echo "补编完成 FAIL=$FAIL"
grep -c "error" /tmp/common_err2.log 2>/dev/null || echo 0
echo ""
echo "=== 2. 重打包 ==="
ar rcs libcommon.a *.o
echo "libcommon.a: $(ar t libcommon.a | wc -l) objects"
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lprotobuf -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -3
ls -la libcommon.a libcommon.so
cp libcommon.so /lib64/ && cp libcommon.so /usr/lib64/ && ldconfig
echo ""
echo "=== 3. 重链 actl + fsd + config_pusher ==="
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f actl fsd
make actl > /tmp/a.log 2>&1; echo "actl exit=$?"
make fsd > /tmp/f.log 2>&1; echo "fsd exit=$?"
ls -la actl fsd 2>/dev/null
cd /root/SOC/ly_server_src/server
rm -f config_pusher
make config_pusher > /tmp/cp.log 2>&1; echo "config_pusher exit=$?"
ls -la config_pusher 2>/dev/null
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