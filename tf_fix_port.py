import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('check current config', 'grep -E "port:|psk:|id:" /Agent/data/config'),
    ('MySQL check port', "mysql -uroot -proot ly -e 'select id,name,port,tls_psk from t_device' 2>/dev/null"),
    ('write correct config', r"""cat > /Agent/data/config << 'EOFCFG'
controller {
  host: "127.0.0.1"
  port: "10081"
}
dev {
  id: 1
  name: "\351\273\230\350\256\244\350\256\276\345\244\207"
  type: "netflow"
  model: ""
  agentid: 1
  ip: "127.0.0.1"
  port: 9995
  disabled: false
  flowtype: "netflow"
  pcap_level: 0
  temp: "V9,IPV4"
  filter: ""
  interface: "ens33"
  psk: "43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa"
}
EOFCFG
echo "written: $(wc -c < /Agent/data/config) bytes"; grep "port:" /Agent/data/config"""),
    ('verify GET', 'REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null | grep -E "port:|psk:"'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()