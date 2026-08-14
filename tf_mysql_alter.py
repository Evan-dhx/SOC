import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("MySQL t_device ALTER", r"""
mysql -uroot -ppassword123 server -e "
ALTER TABLE t_device
  ADD COLUMN IF NOT EXISTS tls_psk VARCHAR(128) DEFAULT '' AFTER interface,
  ADD COLUMN IF NOT EXISTS tls_status VARCHAR(16) DEFAULT '' AFTER tls_psk,
  ADD COLUMN IF NOT EXISTS tls_last_seen BIGINT DEFAULT 0 AFTER tls_status;
DESC t_device;
" 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()