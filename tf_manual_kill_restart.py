import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. New actl has 9996 refs ===')
i, o, e = c.exec_command("strings /Agent/cmd/actl | grep 9996 | head -5", timeout=10)
print(o.read().decode().strip())

print()
print('=== 2. New actl has full tsensor path ===')
i, o, e = c.exec_command("strings /Agent/cmd/actl | grep 'tsensor' | head -5", timeout=10)
print(o.read().decode().strip())

print()
print('=== 3. Check actl binary location ===')
i, o, e = c.exec_command("ls -la /Agent/cmd/actl /Agent/cmd/actl.bak 2>/dev/null; md5sum /Agent/cmd/actl", timeout=10)
print(o.read().decode().strip())

print()
print('=== 4. Manual: kill tsensor, check, restart ===')
script = "#!/bin/bash\n"
script += "echo '=== Before ==='\n"
script += "ps aux | grep tsensor | grep -v grep || echo '(none)'\n"
script += "echo ''\n"
script += "echo '=== Kill tsensor ==='\n"
script += "PID=$(ps -ef | grep tsensor | grep -v grep | awk '{print $2}')\n"
script += "echo \"Found PID: $PID\"\n"
script += "if [ -n \"$PID\" ]; then kill -9 $PID 2>/dev/null; echo 'Killed'; fi\n"
script += "sleep 1\n"
script += "echo ''\n"
script += "echo '=== After kill ==='\n"
script += "ps aux | grep tsensor | grep -v grep || echo '(no tsensor)'\n"
script += "echo ''\n"
script += "echo '=== Start tsensor ==='\n"
script += "/usr/local/bin/tsensor -i ens192 -n 127.0.0.1:9996 -T '%IN_SRC_MAC %OUT_DST_MAC %IPV4_SRC_ADDR %IPV4_DST_ADDR %PROTOCOL %L4_SRC_PORT %L4_DST_PORT %TCP_FLAGS %SRC_TOS %IN_PKTS %IN_BYTES %FIRST_SWITCHED %LAST_SWITCHED' -e 0 -w 32768 -G &>/dev/null &\n"
script += "sleep 3\n"
script += "echo ''\n"
script += "echo '=== After start ==='\n"
script += "ps aux | grep tsensor | grep -v grep || echo '(no tsensor)'\n"
script += "echo ''\n"
script += "echo '=== tsensor.conf ==='\n"
script += "cat /Agent/etc/tsensor.conf 2>/dev/null || echo '(no file)'\n"

i, o, e = c.exec_command("cat > /tmp/manual_test.sh << 'ENDSH'\n" + script + "\nENDSH\nchmod +x /tmp/manual_test.sh && bash /tmp/manual_test.sh", timeout=30)
print(o.read().decode().strip()[:2000])

time.sleep(3)

print()
print('=== 5. Final state ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:300])

c.close()