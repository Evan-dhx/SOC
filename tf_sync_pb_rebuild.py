import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("同步 pb 文件 + 重编译插件", r"""
echo "=== 1. 同步 pb 头文件（3.21.9） ==="
cp /root/SOC/ly_analyser_src/common/*.pb.h /root/SOC/ly_server_src/common/
cp /root/SOC/ly_analyser_src/common/*.pb.cc /root/SOC/ly_server_src/common/
echo "同步完成:"
ls /root/SOC/ly_server_src/common/*.pb.h | wc -l
grep -c "SetNoArena" /root/SOC/ly_server_src/common/mo.pb.h
echo ""
echo "=== 2. 重编译全部插件 ==="
cd /root/SOC/ly_server_src/lib
make 2>&1 | grep -E "error|Error|\.so$|g\+\+" | tail -20
echo ""
echo "=== 3. 符号检查 ==="
for f in config_event.so config_mo.so config_agent.so config_bwlist.so config_user.so config_internalip.so config_internalsrv.so; do
  CNT=$(LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r $f 2>&1 | grep -c "undefined")
  echo "$f: $CNT undefined"
done
echo ""
echo "=== 4. 部署 ==="
cp config_event.so config_mo.so config_agent.so config_bwlist.so config_user.so config_internalip.so config_internalsrv.so /Server/lib/
ls -la /Server/lib/config_*.so | grep -v bak | awk '{print $6, $7, $8, $9}'
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
