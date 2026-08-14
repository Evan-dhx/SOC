import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Use TF's bundled protoc or protobuf-3.8.0 protoc
protoc_paths = [
    '/root/build_deps/protobuf-3.8.0/src/protoc',
    '/root/build_deps/protobuf-3.8.0/src/.libs/protoc',
    '/root/build_deps/tf/tensorflow/contrib/makefile/gen/protobuf/bin/protoc',
]

print('=== Try each protoc ===')
for pp in protoc_paths:
    i, o, e = c.exec_command(f"{pp} --version 2>&1", timeout=10)
    out = o.read().decode().strip() + e.read().decode().strip()
    print(f'  {pp}: {out[:100]}')

print()
print('=== Generate pb files with protobuf-3.8.0 protoc ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && /root/build_deps/protobuf-3.8.0/src/protoc cache.proto topn.proto config.proto mo.proto event.proto policy.proto feature.proto ctl.proto event_feature.proto domaininfo.proto evidence.proto --cpp_out=. 2>&1", timeout=60)
print(o.read().decode().strip()[:500])
err = e.read().decode().strip()
if err: print('ERR:', err[:500])

print()
print('=== Verify config.pb.h has psk ===')
i, o, e = c.exec_command("grep 'psk' /root/SOC/ly_analyser_src/common/config.pb.h 2>/dev/null | head -3", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== Build libcommon.so ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && make -j4 2>&1 | tail -10", timeout=120)
print(o.read().decode().strip()[:2000])

print()
print('=== Verify new libcommon.so ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_analyser_src/common/libcommon.so && md5sum /root/SOC/ly_analyser_src/common/libcommon.so && strings /root/SOC/ly_analyser_src/common/libcommon.so | grep -c 'psk'", timeout=10)
print(o.read().decode().strip())

c.close()