import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Fixing nflowcache.c ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Backup
cp nflowcache.c nflowcache.c.orig 2>/dev/null || true

# Fix 1: ALIGN_BYTES macro - anonymous struct in offsetof not allowed in C++11+
# Replace: #define ALIGN_BYTES (offsetof (struct { char x; uint64_t y; }, y) - 1)
# With: a simpler calculation
sed -i 's|#define ALIGN_BYTES (offsetof (struct { char x; uint64_t y; }, y) - 1)|#define ALIGN_BYTES (sizeof(uint64_t) - 1)|' nflowcache.c

# Fix 2: void pointer arithmetic - cast to char* first
# keymem += sizeof(uint64_t) -> keymem = (char*)keymem + sizeof(uint64_t)
sed -i 's|keymem += sizeof(uint64_t)|keymem = (void*)((char*)keymem + sizeof(uint64_t))|' nflowcache.c
sed -i 's|keymem += sizeof(uint32_t)|keymem = (void*)((char*)keymem + sizeof(uint32_t))|' nflowcache.c
sed -i 's|keymem += sizeof(uint16_t)|keymem = (void*)((char*)keymem + sizeof(uint16_t))|' nflowcache.c
sed -i 's|keymem += sizeof(uint8_t)|keymem = (void*)((char*)keymem + sizeof(uint8_t))|' nflowcache.c

# Fix 3: Other void pointer arithmetic at line 266
# p = handle->memblock[handle->CurrentBlock] + handle->Allocted;
sed -i 's|p = handle->memblock\[handle->CurrentBlock\] + handle->Allocted;|p = (void*)((char*)(handle->memblock[handle->CurrentBlock]) + handle->Allocted);|' nflowcache.c

# Also check for similar patterns
grep -n 'keymem +=' nflowcache.c
echo ""
echo "=== Verify ALIGN_BYTES fix ==="
grep -n 'ALIGN_BYTES' nflowcache.c

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -30
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check nfdump ==="
ls -la /Agent/bin/nf* 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
