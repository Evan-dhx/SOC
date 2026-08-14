import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Clean everything first
print('=== Clean ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && make clean 2>&1 | tail -3", timeout=30)
print(o.read().decode().strip())

# Step 2: Try running bazel protoc with a wrapper script
print()
print('=== Try bazel protoc ===')
script = """#!/bin/bash
# First try: LD_LIBRARY_PATH to the protobuf libs in bazel
BAZEL_DIR="/root/.cache/bazel/_bazel_root/efb88f6336d9c4a18216fb94287b8d97"
PROTOC="$BAZEL_DIR/execroot/org_tensorflow/bazel-out/k8-opt/bin/external/com_google_protobuf/protoc"

# Try multiple LD_LIBRARY_PATH combinations
for LIBPATH in \\
    "$BAZEL_DIR/execroot/org_tensorflow/bazel-out/k8-opt/bin/external/com_google_protobuf" \\
    "/usr/local/lib" \\
    ""; do
    echo "Trying LD_LIBRARY_PATH=$LIBPATH"
    if [ -n "$LIBPATH" ]; then
        LD_LIBRARY_PATH="$LIBPATH" $PROTOC --version 2>&1 && echo "SUCCESS" && exit 0
    else
        $PROTOC --version 2>&1 && echo "SUCCESS" && exit 0
    fi
done
echo "ALL_FAILED"
"""

i, o, e = c.exec_command("cat > /tmp/try_protoc.sh << 'SCRIPT'\n" + script + "\nSCRIPT\nchmod +x /tmp/try_protoc.sh && bash /tmp/try_protoc.sh", timeout=30)
print(o.read().decode().strip())

c.close()