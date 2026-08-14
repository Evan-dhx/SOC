import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what libcommon.so is linked
i, o, e = c.exec_command('ls -la /lib64/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.so /root/SOC/ly_server_src/common/libcommon.so 2>/dev/null', timeout=30)
print('libcommon.so:', o.read().decode()[:300])

# Manually compile config.pb.cc and build libcommon.so
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && test -f config.pb.o && ls -la config.pb.o; echo ---; g++ -c -Wall -fPIC -g -std=c++17 -O2 -I. -I/usr/local/include config.pb.cc -o config.pb.o 2>&1 | head -5; echo EX=$?', timeout=120)
r = o.read().decode()
print('Compile pb:', r[:500])
if 'Error' not in r and 'error' not in r.lower():
    i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && cat Makefile | grep "libcommon.so" | head -3', timeout=30)
    print('libcommon.so rule:', o.read().decode()[:200])
    # Try building libcommon
    i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && make libcommon.so 2>&1 | tail -10', timeout=120)
    print('libcommon.so build:', o.read().decode()[:500])
    # Deploy
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/common/libcommon.so /lib64/ 2>/dev/null; echo EX=$?', timeout=30)
    print('Deploy:', o.read().decode()[:100])
c.close()