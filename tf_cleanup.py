import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what pgrep finds
cmd = 'pgrep -f "bazel build" 2>&1; echo "exit: $?"'
stdin, stdout, stderr = client.exec_command(cmd)
print('pgrep result:', stdout.read().decode('utf-8', errors='replace'))

# Check all bazel-related processes
stdin, stdout, stderr = client.exec_command('ps aux | grep -i bazel')
print('All bazel processes:')
print(stdout.read().decode('utf-8', errors='replace'))

# Check screen sessions
stdin, stdout, stderr = client.exec_command('screen -ls 2>&1')
print('Screen sessions:')
print(stdout.read().decode('utf-8', errors='replace'))

# Kill screen session first
stdin, stdout, stderr = client.exec_command('screen -S tf_build -X quit 2>&1')
print('Screen quit:', stdout.read().decode('utf-8', errors='replace'))

# Kill any remaining bazel-related processes
stdin, stdout, stderr = client.exec_command('pkill -9 -f "bazel" 2>&1; sleep 2; ps aux | grep bazel | grep -v grep')
out = stdout.read().decode('utf-8', errors='replace')
print('After kill:', out if out.strip() else 'All bazel processes killed')

# Verify pgrep no longer matches
cmd = 'pgrep -f "bazel build" 2>&1; echo "exit: $?"'
stdin, stdout, stderr = client.exec_command(cmd)
print('pgrep after cleanup:', stdout.read().decode('utf-8', errors='replace'))

# Verify build artifacts exist
stdin, stdout, stderr = client.exec_command('ls -lh /root/tensorflow/bazel-bin/tensorflow/libtensorflow_cc.so /root/tensorflow/bazel-bin/tensorflow/libtensorflow_framework.so 2>&1')
print('Build artifacts:')
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
