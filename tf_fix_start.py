import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Use sftp to upload the fixed tsensor_start.sh
content = '''#!/bin/bash
CONF=/Agent/etc/tsensor.conf
if [ ! -f "$CONF" ]; then echo "tsensor.conf not found"; exit 1; fi
. "$CONF"
CMD="/usr/local/bin/tsensor -i $interface -n $collector -T \\"$template\\" -e 0 -w 32768"
export PATH="/home/Agent/bin:$PATH"
if [ -n "$psk" ] && [ "$psk" != "none" ]; then
  DEVID=${devid:-1}
  TLS_PORT=$((19995 + DEVID))
  /home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:$TLS_PORT -i "${name:-$interface}" -k "$psk" -d
fi
if [ -n "$filter" ] && [ "$filter" != "none" ]; then
  CMD="$CMD -f \\"$filter\\""
fi
if [ "$pcap_level" != "0" ] && [ -n "$pcap_level" ]; then
  mkdir -p /data/cap/1
  CMD="$CMD -k $pcap_level -K /data/cap/1"
fi
echo "tsensor start: $CMD"
exec bash -c "$CMD"
'''

sftp = c.open_sftp()
with sftp.open('/Agent/etc/tsensor_start.sh', 'w') as f:
    f.write(content)
sftp.close()
print('Uploaded tsensor_start.sh')

# Restart tsensor
i, o, e = c.exec_command('systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor; echo ---; ps -e | grep -E "tsensor|nftls|fcapd|fsd" | head -10', timeout=30)
print(o.read().decode()[:800])
err = e.read().decode()[:300]
if err: print('STDERR:', err)

c.close()