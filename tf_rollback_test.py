import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ============ 最终验证：回滚验证 ============
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== 回滚验证：清除 psk，切换回明文 ===")

# 1. 写回无 psk 的配置
i,o,e = c.exec_command(r"""cat > /Agent/data/config << 'EOFCFG'
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
  interface: "ens192"
}
EOFCFG
grep "psk:" /Agent/data/config || echo "psk removed OK"
wc -c /Agent/data/config""", timeout=30)
print(o.read().decode()[:500])

# 2. 清除 tsensor.conf 中的 psk
i,o,e = c.exec_command("""sed -i '/^psk=/d' /Agent/etc/tsensor.conf; grep psk /Agent/etc/tsensor.conf || echo 'psk removed from tsensor.conf'""", timeout=30)
print(o.read().decode()[:300])

# 3. kill nftls processes
i,o,e = c.exec_command("""pkill nftls 2>/dev/null; sleep 1; ps -e | grep -c nftls || echo 'nftls killed'""", timeout=30)
print(o.read().decode()[:200])

# 4. Restart tsensor
i,o,e = c.exec_command("""sed -i 's|collector=.*|collector=127.0.0.1:9995|' /Agent/etc/tsensor.conf; grep collector /Agent/etc/tsensor.conf; systemctl restart tsensor 2>&1; sleep 3; systemctl is-active tsensor""", timeout=30)
print(o.read().decode()[:300])

# 5. Check processes
i,o,e = c.exec_command("ps -e | grep -E 'tsensor|nftls|fcapd|fsd' | head -5", timeout=30)
print("Processes after rollback:", o.read().decode()[:300])

# 6. Wait 30s and verify data flow
import time
print("Waiting 30s for data...")
time.sleep(30)

i,o,e = c.exec_command("ls -la /data/flow/1/nfcapd.current 2>/dev/null; ss -uln | grep 9995; cat /Agent/etc/nftls.status 2>/dev/null || echo 'no nftls status'", timeout=30)
print("Rollback verification:", o.read().decode()[:500])

c.close()
print("\n=== 回滚验证完成 ===")