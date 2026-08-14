import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Adding all required static libs to nfdump ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Use all agent static libs + whole-archive protobuf
AGENT_DIR=/root/SOC/ly_analyser_src/agent
NEW_LIBS="-Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive ${AGENT_DIR}/flow/flow_filter_noai.a ${AGENT_DIR}/data/data.a ${AGENT_DIR}/model/model.a ${AGENT_DIR}/config/config.a ${AGENT_DIR}/utils/utils.a ${AGENT_DIR}/dump/libnfdump.a -lcommon -lboost_regex -lcppdb -lcurl -lresolv -lpthread"

# Replace LIBS line
sed -i "s|^LIBS = .*|LIBS = ${NEW_LIBS}|" Makefile

echo "Updated LIBS:"
grep '^LIBS' Makefile

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -15
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Final check ==="
ls -la /Agent/bin/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
