import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Compile all req files into libcommon", r"""
echo "=== 1. 检查 common 中所有 req 文件 ==="
ls /root/SOC/ly_analyser_src/common/*_req.cpp 2>/dev/null
echo ""
echo "=== 2. 编译缺失的 req 文件 ==="
cd /root/SOC/ly_analyser_src/common
for f in *_req.cpp; do
  base=$(basename $f .cpp)
  if [ ! -f "$base.o" ]; then
    echo ">>> 编译 $f"
    g++ -c -Wall -g -fPIC -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o $base.o $f 2>&1 | grep -E "error:" | head -3
    echo "    $? -> $base.o"
  else
    echo "跳过 $base.o（已存在）"
  fi
done
echo ""
echo "=== 3. 重新打包 libcommon ==="
rm -f libcommon.a libcommon.so
ar rcs libcommon.a *.o
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive -L/usr/local/lib -L/usr/lib64 2>&1 | head -5
echo "Link exit: $?"
echo ""
echo "=== 4. 验证关键符号 ==="
nm -D libcommon.so | grep -cE "ParseWebReq|ParseFeatureReq|ParseEventFeatureReq|ParseEvidenceReq|stAddWhere"
echo ""
echo "=== 5. 安装 ==="
cp libcommon.so /lib64/
cp libcommon.so /usr/lib64/
cp libcommon.so /Agent/lib/
ldconfig
echo "安装完成"
"""),

    ("Rebuild remaining CGI", r"""
echo "=== 6. 重新编译 event/feature/event_feature/evidence ==="
cd /root/SOC/ly_server_src/server
rm -f event feature event_feature evidence
make event feature event_feature evidence 2>&1 | tail -8
echo "Exit: $?"
ls -lh event feature event_feature evidence 2>/dev/null | awk '{print $5, $9}'
echo ""
echo "=== 7. 部署 ==="
cp event feature event_feature evidence mo internalip bwlist locinfo geoinfo portinfo ipinfo config auth sctl /Server/www/d/
cp config_pusher gen_event /Server/bin/
echo "部署完成"
ls -la /Server/www/d/ | awk '{print $5, $9}' | head -18
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
