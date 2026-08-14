import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Generate pb files using bazel protoc
print('=== Generate pb files ===')
i, o, e = c.exec_command(
    "cd /root/SOC/ly_analyser_src/common && "
    "LD_LIBRARY_PATH=/root/.cache/bazel/_bazel_root/efb88f6336d9c4a18216fb94287b8d97/execroot/org_tensorflow/bazel-out/k8-opt/bin/external/com_google_protobuf "
    "/root/.cache/bazel/_bazel_root/efb88f6336d9c4a18216fb94287b8d97/execroot/org_tensorflow/bazel-out/k8-opt/bin/external/com_google_protobuf/protoc "
    "cache.proto topn.proto config.proto mo.proto event.proto policy.proto feature.proto ctl.proto event_feature.proto "
    "domaininfo.proto evidence.proto --cpp_out=. 2>&1",
    timeout=60)
print(o.read().decode().strip()[:500])

print()
print('=== Verify psk in config.pb.h ===')
i, o, e = c.exec_command("grep 'psk' /root/SOC/ly_analyser_src/common/config.pb.h | head -3", timeout=10)
print(o.read().decode().strip())

print()
print('=== Build libcommon.so ===')
i, o, e = c.exec_command(
    "cd /root/SOC/ly_analyser_src/common && make -j4 2>&1 | tail -10",
    timeout=180)
print(o.read().decode().strip()[:2000])

print()
print('=== Verify libcommon.so ===')
i, o, e = c.exec_command(
    "ls -la /root/SOC/ly_analyser_src/common/libcommon.so && "
    "md5sum /root/SOC/ly_analyser_src/common/libcommon.so && "
    "strings /root/SOC/ly_analyser_src/common/libcommon.so | grep -c 'psk'",
    timeout=10)
print(o.read().decode().strip())

print()
print('=== Install to system paths ===')
cmds = [
    "cp /root/SOC/ly_analyser_src/common/libcommon.so /usr/lib64/libcommon.so",
    "cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Agent/lib/libcommon.so",
    "cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Server/lib/libcommon.so",
    "echo INSTALLED",
]
i, o, e = c.exec_command(" && ".join(cmds), timeout=10)
print(o.read().decode().strip())

c.close()