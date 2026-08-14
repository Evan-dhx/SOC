import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find absl headers", "find /root/tensorflow/bazel-tensorflow/external -maxdepth 1 -name '*absl*' -type d 2>/dev/null"),
    ("Check absl structure", "ls /root/tensorflow/bazel-tensorflow/external/com_google_absl/ 2>/dev/null | head -10"),
    ("Check absl/strings", "ls /root/tensorflow/bazel-tensorflow/external/com_google_absl/absl/strings/ 2>/dev/null | head -10"),
    ("Find nsync headers", "find /root/tensorflow/bazel-tensorflow/external -maxdepth 1 -name '*nsync*' -type d 2>/dev/null"),
    ("Find protobuf headers", "find /root/tensorflow/bazel-tensorflow/external -maxdepth 1 -name '*protobuf*' -type d 2>/dev/null"),
    ("Check protobuf src", "ls /root/tensorflow/bazel-tensorflow/external/com_google_protobuf/src/google/protobuf/ 2>/dev/null | head -5"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()
