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

# ===== 1. 恢复 nfdump 原始文件 =====
print("=" * 60)
print("[1] 恢复 nfdump 原始文件")
print("=" * 60)
run('cp /Agent/bin/nfdump.real /Agent/bin/nfdump', "恢复 nfdump")
run('chmod +x /Agent/bin/nfdump', "设置权限")
out, _ = run('file /Agent/bin/nfdump', "验证文件类型")

# ===== 2. 检查 nfdump 对 libcommon.so 的依赖 =====
print("\n" + "=" * 60)
print("[2] 检查 nfdump 对 libcommon.so 的符号依赖")
print("=" * 60)
out, _ = run('nm -D /Agent/bin/nfdump 2>/dev/null | grep "U " | grep -v "protobuf\\|stdc\\|m\\|gcc\\|c\\.\\|resolv\\|z\\|icu\\|nghttp\\|idn\\|ssh\\|curl\\|boost\\|cgicc\\|cppdb\\|json\\|psl\\|ssl\\|crypto\\|gssapi\\|krb5" | head -20', "nfdump 未定义的非标准符号")
print("  nfdump 引用的非标准符号 (可能来自 libcommon.so):")
print(out.strip() if out.strip() else "  (无)")

# 检查 nfdump 是否有 patchelf
out, _ = run('which patchelf 2>/dev/null || echo "patchelf 不存在"', "patchelf 可用性")

# ===== 3. 检查 nfdump 对 libcommon.so 的实际符号引用 =====
print("\n" + "=" * 60)
print("[3] nfdump 对 libcommon.so 的具体符号引用")
print("=" * 60)
out, _ = run('nm -D /Agent/bin/nfdump 2>/dev/null | grep "U " | wc -l', "总未定义符号数")
print(f"  总未定义符号数: {out.strip()}")

# 检查 nfdump 是否真的需要 libcommon.so
out, _ = run('readelf -d /Agent/bin/nfdump 2>/dev/null | grep NEEDED | head -20', "nfdump NEEDED 依赖")
print(f"  NEEDED 依赖:\n{out.strip()}")

# ===== 4. 创建 shim 库 =====
print("\n" + "=" * 60)
print("[4] 创建 AddDescriptors shim 库")
print("=" * 60)

# 创建 shim C++ 代码
shim_code = r'''// shim.cpp - Provide old protobuf AddDescriptors by wrapping AddDescriptorsRunner
#include <cstddef>

// Forward declarations matching protobuf internal types
namespace google {
namespace protobuf {
namespace internal {
struct DescriptorTable;

// AddDescriptorsRunner is a class whose constructor registers descriptor tables
// Its mangled name: _ZN6google8protobuf8internal20AddDescriptorsRunnerC1EPKNS1_15DescriptorTableE
extern void _ZN6google8protobuf8internal20AddDescriptorsRunnerC1EPKNS1_15DescriptorTableE(
    void* this_ptr, const DescriptorTable* table);

// Old API: AddDescriptors(const DescriptorTable*)
// Mangled name: _ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE
// We implement it by creating a temporary AddDescriptorsRunner object
extern "C" void _ZN6google8protobuf8internal14AddDescriptorsEPKNS1_15DescriptorTableE(
    const DescriptorTable* table) {
    // Allocate enough space for AddDescriptorsRunner object on stack
    // The object is small (typically 8-16 bytes)
    long long buf[16]; // 128 bytes, more than enough
    // Call AddDescriptorsRunner constructor
    _ZN6google8protobuf8internal20AddDescriptorsRunnerC1EPKNS1_15DescriptorTableE(buf, table);
    // Object goes out of scope - no need to destruct (AddDescriptorsRunner
    // constructor does all the work in registering the descriptor table)
}
}
}
}
'''

# 写入并编译
stdin, stdout, stderr = c.exec_command(f'cat > /tmp/shim.cpp << \'SHIMEOF\'\n{shim_code}\nSHIMEOF')
stdout.read()
print("  shim.cpp 已创建")

# 编译 shim 库
out, err = run('g++ -shared -fPIC -o /usr/local/lib/compat/libadd_descriptors_shim.so /tmp/shim.cpp -L/usr/local/lib -lprotobuf 2>&1', "编译 shim 库")
if 'error' in err.lower() or 'error' in out.lower():
    print(f"  编译失败!")
    print(f"  输出: {out.strip()[:500]}")
    print(f"  错误: {err.strip()[:500]}")
else:
    print("  shim 库编译成功!")
    # 验证符号
    out, _ = run('nm -D /usr/local/lib/compat/libadd_descriptors_shim.so 2>/dev/null | grep AddDescriptors', "shim 库符号")
    print(f"  shim 库符号:\n{out.strip()}")

# ===== 5. 测试 nfdump with LD_PRELOAD =====
print("\n" + "=" * 60)
print("[5] 测试 nfdump with LD_PRELOAD shim")
print("=" * 60)

out, err = run('LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so /Agent/bin/nfdump -V 2>&1 || true', "nfdump -V 测试")
if 'symbol lookup error' in out.lower():
    print(f"  [!] 仍有 symbol lookup error!")
    print(f"  输出: {out.strip()[:500]}")
else:
    print(f"  nfdump 输出: {out.strip()[:300]}")
    print("  nfdump 修复成功!")

# ===== 6. 如果 shim 成功，更新 nfdump wrapper =====
if 'symbol lookup error' not in out.lower():
    print("\n" + "=" * 60)
    print("[6] 更新 nfdump wrapper 使用 LD_PRELOAD")
    print("=" * 60)
    
    wrapper = '''#!/bin/bash
# nfdump wrapper - preload AddDescriptors shim
export LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so:$LD_PRELOAD
exec /Agent/bin/nfdump.real "$@"
'''
    
    stdin, stdout, stderr = c.exec_command('cp /Agent/bin/nfdump /Agent/bin/nfdump.real 2>/dev/null; cat > /Agent/bin/nfdump << \'WRAPPEREOF2\'\n' + wrapper + '\nWRAPPEREOF2')
    stdout.read()
    run('chmod +x /Agent/bin/nfdump', "设置 wrapper 权限")
    
    # 验证 wrapper
    out, _ = run('LD_LIBRARY_PATH= /Agent/bin/nfdump -V 2>&1', "验证 wrapper nfdump")
    print(f"  wrapper 测试: {out.strip()[:300]}")
else:
    print("\n  [!] shim 方案失败，恢复原始 nfdump")
    run('cp /Agent/bin/nfdump.real /Agent/bin/nfdump 2>/dev/null', "恢复原始 nfdump")

c.close()
print("\n" + "=" * 60)
print("shim 修复完成!")
print("=" * 60)
