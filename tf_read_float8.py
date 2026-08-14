import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# First restore from backup
stdin, stdout, stderr = client.exec_command('cp /usr/local/include/tf/tensorflow/tsl/platform/float8.h.backup /usr/local/include/tf/tensorflow/tsl/platform/float8.h')
stdout.read()

# Read the file content
stdin, stdout, stderr = client.exec_command('cat /usr/local/include/tf/tensorflow/tsl/platform/float8.h')
content = stdout.read().decode('utf-8', errors='replace')

# Find the key markers
lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# Find ConvertFrom and ConvertTo methods
for i, line in enumerate(lines):
    if 'ConvertFrom' in line and 'static' in line:
        print(f"Line {i+1}: {line.strip()}")
    if 'ConvertTo' in line and 'static' in line:
        print(f"Line {i+1}: {line.strip()}")
    if 'class float8_base' in line:
        print(f"Line {i+1}: {line.strip()}")
    if 'class float8_e4m3fn' in line:
        print(f"Line {i+1}: {line.strip()}")
    if 'class float8_e5m2' in line:
        print(f"Line {i+1}: {line.strip()}")
    if 'struct ConvertImpl;' in line:
        print(f"Line {i+1}: {line.strip()}")

# Find the generic ConvertImpl that catches all (line ~556 area)
for i, line in enumerate(lines):
    if 'struct ConvertImpl<From, To' in line:
        print(f"Line {i+1}: {line.strip()}")

client.close()
