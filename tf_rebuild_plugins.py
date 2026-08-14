import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("补 t_url_attack_type + 重编译插件", r"""
echo "=== 1. 补 t_url_attack_type ==="
mysql -uroot -ppassword123 server -e "INSERT INTO t_url_attack_type(id, \`desc\`) VALUES (1,'sql_inject'),(2,'xss'),(3,'reso_explore'),(4,'visit_admin'),(5,'pull_db'); SELECT COUNT(*) FROM t_url_attack_type;" 2>&1
echo ""
echo "=== 2. 备份旧插件 ==="
cd /root/SOC/ly_server_src/lib
for f in config_event.so config_mo.so config_agent.so config_bwlist.so config_user.so config_internalip.so config_internalsrv.so; do
  [ -f /Server/lib/$f ] && cp /Server/lib/$f /Server/lib/$f.bak_old
done
echo "备份完成"
echo ""
echo "=== 3. bazel protoc 重新生成 .pb.cc ==="
/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc config_event.proto config_agent.proto config_bwlist.proto config_user.proto --cpp_out=. 2>&1
ls -la config_event.pb.cc config_agent.pb.cc config_bwlist.pb.cc config_user.pb.cc | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 4. 更新 Makefile（C++17 + common 头文件） ==="
sed -i 's|CXXFLAGS=-Wall -fPIC -shared -g -std=c++0x|CXXFLAGS=-Wall -fPIC -shared -g -std=c++17 -fpermissive|' Makefile
sed -i 's|INCS=-I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I.|INCS=-I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/usr/local/include -I/root/SOC/ly_analyser_src/common|' Makefile
grep -E "^CXXFLAGS|^INCS" Makefile
echo ""
echo "=== 5. 重编译全部插件 ==="
make clean 2>/dev/null
make 2>&1 | tail -15
echo ""
echo "=== 6. 检查符号 ==="
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r config_event.so 2>&1 | grep -c "undefined" || echo "0 undefined"
ls -la config_event.so config_mo.so config_agent.so
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:3000]}")

client.close()
