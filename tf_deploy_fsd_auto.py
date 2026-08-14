import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Check and rebuild fsd if needed
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && grep -n "nftls" fsd.cpp | head -5', timeout=30)
print('fsd nftls paths:', o.read().decode()[:500])

# Step 2: Force recompile with latest fix
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f fsd.o && make fsd 2>&1 | tail -5', timeout=120)
print('Compile:', o.read().decode()[:300])

i, o, e = c.exec_command('ls -la /root/SOC/ly_analyser_src/agent/handlers/fsd', timeout=30)
print('Binary:', o.read().decode()[:200])

# Step 3: Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/fsd /home/Agent/bin/ 2>/dev/null; ls -la /home/Agent/bin/fsd', timeout=30)
print('Deployed:', o.read().decode()[:200])

# Step 4: Kill old fsd if running, kill nftls to test auto-recovery
i, o, e = c.exec_command('pkill -x fsd 2>/dev/null; pkill nftls 2>/dev/null; sleep 2; ps -e | grep -c nftls; ps -e | grep -c fsd', timeout=30)
print('Killed old:', o.read().decode()[:100])

# Step 5: Start fsd
i, o, e = c.exec_command('cat > /tmp/fsd.sh << "SCRIPT"\n#!/bin/bash\n/home/Agent/bin/fsd > /dev/null 2>&1 &\nsleep 3\necho "fsd started: $(pgrep -x fsd)"\nSCRIPT\nbash /tmp/fsd.sh', timeout=30)
print('Start fsd:', o.read().decode()[:200])

time.sleep(3)

# Step 6: Check what fsd is doing
i, o, e = c.exec_command('ps -e | grep -E "fsd|nftls|fcapd|tsensor" | head -8', timeout=30)
print('Processes:', o.read().decode()[:500])

c.close()

# Step 7: Wait for fsd cycle and check
time.sleep(70)

c2 = paramiko.SSHClient()
c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c2.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c2.exec_command('echo === log ===; tail -10 /Agent/data/log; echo === nftls ===; ps -e | grep nftls | head -3; echo === status ===; cat /Agent/etc/nftls.status 2>/dev/null; echo === nfcapd ===; ps -e | grep fcapd', timeout=30)
print(o.read().decode()[:1500])

# Step 8: Kill nftls again and see if fsd recovers it
print('\n--- 测试自动恢复：killing nftls... ---')
i, o, e = c2.exec_command('pkill nftls 2>/dev/null; sleep 5; ps -e | grep nftls | head -3; echo ---; sleep 60; echo === after 60s ===; tail -5 /Agent/data/log; echo; ps -e | grep nftls | head -3', timeout=120)
print(o.read().decode()[:1000])

c2.close()