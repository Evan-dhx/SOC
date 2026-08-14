import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find float8 related files", r"""
echo "=== Find float8 files ==="
find /usr/local/include/tf/tensorflow/tsl/platform -name "float8*" -type f 2>/dev/null
echo ""
echo "=== Check for float8 impl/conversions ==="
find /usr/local/include/tf/tensorflow/tsl -name "*float8*" -type f 2>/dev/null
echo ""
echo "=== Check what includes float8.h ==="
grep -rn "float8.h" /usr/local/include/tf/tensorflow/tsl/platform/*.h 2>/dev/null | grep -v "float8.h:" | head -10
echo ""
echo "=== Check float8.h for ConvertImpl ==="
grep -n "ConvertImpl" /usr/local/include/tf/tensorflow/tsl/platform/float8.h | head -20
"""),

    ("Check if there's a float8 conversions header", r"""
echo "=== Search for ConvertImpl definitions ==="
grep -rn "struct ConvertImpl" /usr/local/include/tf/tensorflow/tsl/platform/ 2>/dev/null | head -20
echo ""
echo "=== Search for float8 conversion specializations ==="
grep -rn "ConvertImpl.*float8" /usr/local/include/tf/tensorflow/tsl/ 2>/dev/null | head -20
"""),

    ("Check if float8_e4m3fn.h or similar exists", r"""
echo "=== Search for float8 type headers ==="
find /usr/local/include/tf/tensorflow/tsl -name "*float8*" -o -name "*f8*" 2>/dev/null
echo ""
echo "=== Check float8.h includes ==="
head -30 /usr/local/include/tf/tensorflow/tsl/platform/float8.h
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
