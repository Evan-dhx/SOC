import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restore TLS encryption mode
for cmd in [
    # 1. Write config with psk
    r"""cat > /Agent/data/config << 'EOFCFG'
controller { host: "127.0.0.1" port: "10081" }
dev {
  id: 1 name: "\351\273\230\350\256\244\350\256\276\345\244\207" type: "netflow"
  model: "" agentid: 1 ip: "127.0.0.1" port: 9995 disabled: false
  flowtype: "netflow" pcap_level: 0 temp: "V9,IPV4" filter: "" interface: "ens192"
  psk: "43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa"
}
EOFCFG
grep "psk:" /Agent/data/config""",
    # 2. Write tsensor.conf with psk and collector=9996
    r"""cat > /Agent/etc/tsensor.conf << 'EOFTS'
interface=ens192
collector=127.0.0.1:9996
template=%IN_SRC_MAC %OUT_DST_MAC %IPV4_SRC_ADDR %IPV4_DST_ADDR %PROTOCOL %L4_SRC_PORT %L4_DST_PORT %TCP_FLAGS %SRC_TOS %IN_PKTS %IN_BYTES %FIRST_SWITCHED %LAST_SWITCHED %DNS_REQ_DOMAIN %DNS_REQ_TYPE %DNS_RES_IP %HTTP_URL %HTTP_REQ_METHOD %HTTP_HOST %HTTP_MIME %HTTP_RET_CODE %HTTP_USER_AGENT %HTTP_COOKIE %FLOW_ID
pcap_level=0
filter=
psk=43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa
EOFTS
grep -E "collector|psk" /Agent/etc/tsensor.conf""",
    # 3. Start nftls server
    'rm -f /Agent/etc/nftls.status; /home/Agent/bin/nftls -m server -l 0.0.0.0:19996 -r 127.0.0.1:9995 -p /Agent/etc/nftls.psk -s /Agent/etc/nftls.status -d 2>&1; sleep 2; ss -tlnp | grep 19996',
    # 4. Start nftls client + tsensor
    '/home/Agent/bin/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19996 -i "默认设备" -k 43ea5d57f3904d99d65a7a51853a3b9b2a88537b4de676aa -d 2>&1; systemctl restart tsensor 2>&1; sleep 3; ss -uln | grep 9996; ps -e | grep -E "tsensor|nftls" | head -5',
    # 5. Verify status
    'sleep 10; cat /Agent/etc/nftls.status 2>/dev/null; echo; ss -tlnp | grep 19996',
]:
    print(f"\n=== {cmd[:50]} ===")
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')[:800]
    err = e.read().decode('utf-8', errors='replace')[:200]
    if out: print(out)
    if err: print('ERR:', err)
c.close()
print("\n=== TLS加密模式已恢复 ===")