import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Manually link libcommon.so with new config.pb.o
# First, check what .o files are in the current libcommon.a
i, o, e = c.exec_command('ar t /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null', timeout=30)
objs = o.read().decode().strip().split('\n')
print(f'Objects in libcommon.a: {len(objs)}')

# Manually compile config.pb.o with the new pb files
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && g++ -c -Wall -fPIC -g -std=c++17 -O2 -I. -I/usr/local/include config.pb.cc -o config.pb_new.o 2>&1', timeout=120)
print('Compile config.pb.o:', o.read().decode()[:200])

# Extract all .o files from libcommon.a, replace config.pb.o, and relink
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && mkdir -p /tmp/libcommon_build && cd /tmp/libcommon_build && ar x /root/SOC/ly_analyser_src/common/libcommon.a && cp /root/SOC/ly_analyser_src/common/config.pb_new.o config.pb.o && ar rcs /root/SOC/ly_analyser_src/common/libcommon_new.a *.o && ls -la /root/SOC/ly_analyser_src/common/libcommon_new.a', timeout=120)
print('New .a:', o.read().decode()[:300])

# Now build libcommon.so from the static library and shared objects
# Get the linker command from Makefile
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && g++ -shared -Wl,--whole-archive libcommon_new.a -Wl,--no-whole-archive -lprotobuf -lcppdb -lcgicc -lcurl -lboost_regex -o libcommon_new.so 2>&1', timeout=120)
r = o.read().decode()
print('New .so:', r[:300])
if 'Error' not in r and 'error' not in r.lower():
    # Deploy
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/common/libcommon_new.so /lib64/libcommon.so', timeout=30)
    print('Deployed to /lib64/libcommon.so')
    
    # Now rebuild actl - it should use the new libcommon.so at runtime
    i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o actl && make actl 2>&1 | tail -5', timeout=120)
    print('actl rebuild:', o.read().decode()[:300])
    
    # Test
    i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | tail -5', timeout=120)
    print('Push:', o.read().decode()[:500])
    import time
    time.sleep(3)
    i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
    print('tsensor.conf:', o.read().decode()[:200])
c.close()