import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check Tensor wrapper file", "cat /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/CXX11/Tensor"),
    ("Check bazel external eigen", "ls -la /root/tensorflow/bazel-tensorflow/external/eigen_archive/ 2>/dev/null | head -10"),
    ("Eigen CXX11 dir", "ls /root/tensorflow/bazel-tensorflow/external/eigen_archive/unsupported/Eigen/CXX11/ 2>/dev/null | head -10"),
    ("Eigen dir structure", "find /root/tensorflow/bazel-tensorflow/external/eigen_archive -maxdepth 3 -type d 2>/dev/null | head -20"),
    ("Installed eigen3 dir", "ls /usr/local/include/tf/third_party/eigen3/ 2>/dev/null"),
    ("Installed CXX11 dir", "ls /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/CXX11/ 2>/dev/null"),
    ("Installed Eigen dir", "ls /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/ 2>/dev/null | head -10"),
    ("Check if actual Tensor exists", "find /root/tensorflow/bazel-tensorflow/external/eigen_archive/unsupported -name 'Tensor' -type f 2>/dev/null"),
    ("MKL eigen path", "ls /root/tensorflow/bazel-tensorflow/third_party/eigen3/mkl_include/ 2>/dev/null | head -5"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()
