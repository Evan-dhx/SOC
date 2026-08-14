import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find DB_CONF and other DB constants
print("=== define.h DB constants ===")
cmd = r"""
grep -n 'DB_CONF\|SERVER_DB_\|DB_USER\|DB_NAME\|DB_GROUP\|DB_PASS' /root/SOC/ly_server_src/server/define.h 2>/dev/null
echo "---"
grep -rn 'DB_CONF\|SERVER_DB_' /root/SOC/ly_server_src/server/define.h /root/SOC/ly_server_src/common/define.h 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check if DB_CONF file exists
print("\n=== Check DB_CONF locations ===")
cmd2 = r"""
# Common locations for DB config
for f in /etc/ly_server/db.conf /Server/etc/db.conf /Server/db.conf /etc/db.conf /data/db.conf /Agent/etc/db.conf; do
  echo -n "$f: "
  if [ -f "$f" ]; then echo "EXISTS - $(cat $f)"; else echo "NOT FOUND"; fi
done
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Find what DB_CONF actually is by looking at the binary
print("\n=== DB_CONF from binary ===")
cmd3 = r"""
strings /Server/www/d/auth | grep -E '\.conf$|db\.|passwd|mysql' | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the full define.h
print("\n=== server define.h ===")
cmd4 = r"""
cat /root/SOC/ly_server_src/server/define.h
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check common define.h
print("\n=== common define.h ===")
cmd5 = r"""
cat /root/SOC/ly_server_src/common/define.h
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
