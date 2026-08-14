import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch tsensor buffers", r"""
echo "=== 1. 备份源码 ==="
cp /root/tsensor/nprobe.h /root/tsensor/nprobe.h.bak_buf
cp /root/tsensor/export.c /root/tsensor/export.c.bak_buf

echo "=== 2. 扩大 NETFLOW_MAX_BUFFER_LEN 1440 -> 8192 ==="
sed -i 's/#define NETFLOW_MAX_BUFFER_LEN    1440/#define NETFLOW_MAX_BUFFER_LEN    8192/' /root/tsensor/nprobe.h
grep "NETFLOW_MAX_BUFFER_LEN" /root/tsensor/nprobe.h | head -2

echo "=== 3. 扩大 flowBuffer 1600 -> 9000 ==="
sed -i 's/char flowBuffer\[1600\];/char flowBuffer[9000];/' /root/tsensor/export.c
grep -n "flowBuffer\[" /root/tsensor/export.c | head -3

echo "=== 4. 修复截断逻辑（flowsetLen 同步更新） ==="
python3 << 'PYEOF'
path = '/root/tsensor/export.c'
with open(path) as f:
    content = f.read()

old = '''    if((bufLen+readWriteGlobals->bufferLen) >= sizeof(flowBuffer)) {
      static u_char warning_sent = 0;
      
      if(!warning_sent) {
	traceEvent(TRACE_WARNING,
		   "Internal error: too many NetFlow flows per packet (see -m)");
	warning_sent = 1;
      }

      readWriteGlobals->bufferLen = sizeof(flowBuffer)-bufLen-1;
    }

    memcpy(&flowBuffer[bufLen], readWriteGlobals->buffer, readWriteGlobals->bufferLen);'''

new = '''    if((bufLen+readWriteGlobals->bufferLen) >= sizeof(flowBuffer)) {
      static u_char warning_sent = 0;
      
      if(!warning_sent) {
	traceEvent(TRACE_WARNING,
		   "Internal error: too many NetFlow flows per packet (see -m)");
	warning_sent = 1;
      }

      /* Truncate flow data and fix the flowset length so the exported
         packet stays consistent for the collector */
      readWriteGlobals->bufferLen = sizeof(flowBuffer)-bufLen-1;
      len = readWriteGlobals->bufferLen+4;
      pad = padding(len); len += pad;
      flowSet.flowsetLen = htons(len);
      memcpy(&flowBuffer[bufLen-sizeof(flowSet)], &flowSet, sizeof(flowSet));
    }

    memcpy(&flowBuffer[bufLen], readWriteGlobals->buffer, readWriteGlobals->bufferLen);'''

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print("OK: 截断逻辑已修复")
else:
    print("FAIL: 未找到截断代码块")
PYEOF
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
