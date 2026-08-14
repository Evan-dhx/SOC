import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:2000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:500]}")
    return out, err

# ===== 1. 创建汇编 shim =====
print("=" * 60)
print("[1] 创建汇编 shim 库 (内联汇编)")
print("=" * 60)

# 使用内联汇编，避免 C++ 名称修饰
# x86-64 System V ABI:
# AddDescriptors(const DescriptorTable* table):  rdi = table
# AddDescriptorsRunner(this, const DescriptorTable* table): rdi = this, rsi = table
shim_c = r'''/* shim.c - Provide old protobuf AddDescriptors via inline asm wrapper */
__asm__(
    ".text\n"
    ".globl _ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE\n"
    ".type _ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE, @function\n"
    "_ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE:\n"
    "    push %rbx\n"           /* save callee-saved reg */
    "    sub $128, %rsp\n"      /* allocate space for AddDescriptorsRunner object */
    "    mov %rdi, %rsi\n"     /* table (arg0) -> rsi (arg1) */
    "    mov %rsp, %rdi\n"    /* buf -> rdi (arg0 = this) */
    "    call _ZN6google8protobuf8internal20AddDescriptorsRunnerC1EPKNS1_15DescriptorTableE\n"
    "    add $128, %rsp\n"     /* free stack space */
    "    pop %rbx\n"           /* restore */
    "    ret\n"
    ".size _ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE, .-_ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE\n"
);
'''

stdin, stdout, stderr = c.exec_command(f"cat > /tmp/shim.c << 'SHIMEOF'\n{shim_c}\nSHIMEOF")
stdout.read()
print("  shim.c 已创建")

# 编译 shim 库（用 gcc，不是 g++，避免 C++ 名称修饰）
out, err = run('gcc -shared -fPIC -o /usr/local/lib/compat/libadd_descriptors_shim.so /tmp/shim.c 2>&1', "编译 shim 库 (gcc)")
if 'error' in err.lower() or 'error' in out.lower():
    print(f"  编译失败!")
    print(f"  错误: {err.strip()[:500]}")
else:
    print("  shim 库编译成功!")
    out, _ = run('nm -D /usr/local/lib/compat/libadd_descriptors_shim.so 2>/dev/null', "shim 库符号")
    print(f"  符号:\n{out.strip()}")

# ===== 2. 测试 nfdump =====
print("\n" + "=" * 60)
print("[2] 测试 nfdump with LD_PRELOAD shim")
print("=" * 60)

out, err = run('LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so /Agent/bin/nfdump -V 2>&1 || true', "nfdump -V 测试")
if 'symbol lookup error' in out.lower():
    print(f"  [!] 仍有 symbol lookup error!")
    print(f"  输出: {out.strip()[:500]}")
else:
    print(f"  nfdump 输出: {out.strip()[:300]}")
    print("  nfdump symbol lookup error 修复成功!")

# ===== 3. 创建 nfdump wrapper =====
if 'symbol lookup error' not in out.lower():
    print("\n" + "=" * 60)
    print("[3] 创建 nfdump wrapper")
    print("=" * 60)
    
    # 备份原始 nfdump
    out, _ = run('ls /Agent/bin/nfdump.real 2>/dev/null', "检查 nfdump.real 是否存在")
    if 'No such' in out or not out.strip():
        run('cp /Agent/bin/nfdump /Agent/bin/nfdump.real', "备份 nfdump")
    
    wrapper = '''#!/bin/bash
# nfdump wrapper - preload AddDescriptors shim for protobuf compat
export LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so
exec /Agent/bin/nfdump.real "$@"
'''
    
    stdin, stdout, stderr = c.exec_command(f"cat > /Agent/bin/nfdump << 'WRAPPEREOF'\n{wrapper}\nWRAPPEREOF")
    stdout.read()
    run('chmod +x /Agent/bin/nfdump', "设置权限")
    
    # 验证 wrapper
    out, _ = run('cat /Agent/bin/nfdump', "wrapper 内容")
    print(f"  wrapper:\n{out.strip()}")
    
    out, _ = run('/Agent/bin/nfdump -V 2>&1 || true', "验证 wrapper nfdump -V")
    print(f"  测试: {out.strip()[:300]}")
    
    # 测试实际 nfdump 命令
    out, _ = run('/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current -s record -n 10 2>&1 | head -5', "测试 nfdump 实际命令")
    print(f"  nfdump 实际输出: {out.strip()[:300]}")
else:
    print("\n  [!] shim 方案失败，nfdump 保持原始状态")

c.close()
print("\n" + "=" * 60)
print("shim 修复完成!")
print("=" * 60)
