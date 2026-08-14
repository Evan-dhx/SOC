import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("修复 mo_req.cpp 注释块", r"""
cd /root/SOC/ly_analyser_src/common
python3 - <<'PYEOF'
lines = open('mo_req.cpp').readlines()
# 备份
open('mo_req.cpp.bak','w').writelines(lines)
# 行号从 1 开始：379-410 注释化（旧实现第一段），411-439 保持（新定义活代码），439 去掉 */，441-467 注释化
for i in range(0, len(lines)):
    n = i + 1
    if 379 <= n <= 410:
        if not lines[i].startswith('//'):
            lines[i] = '//' + lines[i]
    elif n == 411:
        continue  # 新定义开始，保持活代码
    elif 412 <= n <= 438:
        continue  # 新定义体，保持
    elif n == 439:
        lines[i] = lines[i].replace('}*/', '}')
    elif 441 <= n <= 466:
        if not lines[i].startswith('//'):
            lines[i] = '//' + lines[i]
    elif n == 467:
        lines[i] = lines[i].replace('}*/', '// }')
open('mo_req.cpp','w').writelines(lines)
print("修改完成")
PYEOF
echo "=== 1. 验证修改 ==="
sed -n '378,442p' mo_req.cpp | head -35
echo ""
echo "=== 2. 重新编译 mo_req.o ==="
g++ -c -Wall -g -fPIC -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o mo_req.o mo_req.cpp 2>&1 | head -5
echo "编译退出码: $?"
nm -C mo_req.o | grep -i "getmo"
echo ""
echo "=== 3. 重新打包 libcommon.a + .so ==="
ar rcs libcommon.a mo_req.o
g++ -shared -o libcommon.so *.o -Wl,--whole-archive -lcppdb -lcgicc -lcurl -lboost_regex -Wl,--no-whole-archive 2>&1 | tail -3
nm -D libcommon.so | grep -i "getMoIDs"
cp libcommon.so /lib64/libcommon.so
cp libcommon.so /usr/lib64/libcommon.so
cp libcommon.so /Agent/lib/libcommon.so
cp libcommon.so /home/Agent/lib/libcommon.so
cp libcommon.so /home/Server/lib/libcommon.so
cp libcommon.so /root/SOC/ly_server_src/common/libcommon.so
echo "打包部署完成"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()