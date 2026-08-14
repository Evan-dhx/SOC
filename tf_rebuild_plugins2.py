import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("改用 bazel protoc 重编译插件", r"""
cd /root/SOC/ly_server_src/lib
echo "=== 1. Makefile protoc 改为 bazel 版本 ==="
sed -i 's|^	protoc |	/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc |' Makefile
grep -n "protoc" Makefile | head -3
echo ""
echo "=== 2. 重新 make ==="
make 2>&1 | tail -20
echo ""
echo "=== 3. 检查符号 ==="
for f in config_event.so config_mo.so config_agent.so config_bwlist.so config_user.so config_internalip.so config_internalsrv.so; do
  CNT=$(LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r $f 2>&1 | grep -c "undefined")
  echo "$f: $CNT undefined"
done
echo ""
echo "=== 4. 部署插件 ==="
cp config_event.so config_mo.so config_agent.so config_bwlist.so config_user.so config_internalip.so config_internalsrv.so /Server/lib/
ls -la /Server/lib/config_*.so | awk '{print $6, $7, $8, $9}'
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
