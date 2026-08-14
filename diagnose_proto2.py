import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print(f"{'='*60}")
    print(out.strip() if out.strip() else "(无输出)")
    if err.strip():
        print(f"STDERR: {err.strip()[:500]}")

# ===== 1. 检查是否有二进制需要 AddDescriptorsRunner (新库独有) =====
run('for f in /Agent/bin/nfdump /Agent/bin/indexer /Agent/bin/extractor /Server/bin/config_pusher /Server/www/d/sctl /Agent/cmd/extract_feature /Agent/cmd/extract_event; do echo "--- $f ---"; nm -D $f 2>/dev/null | grep "AddDescriptorsRunner" | head -2; done', "检查 AddDescriptorsRunner 依赖")

# ===== 2. 检查 TensorFlow 库是否依赖动态 protobuf =====
run('find /Agent/lib /Agent/models -name "*.so" -exec sh -c "echo --- {} ---; ldd {} 2>/dev/null | grep protobuf" \\; 2>/dev/null | head -30', "TensorFlow 库 protobuf 依赖")

# ===== 3. 检查 libcommon.so 的 protobuf 符号 =====
run('nm -D /lib64/libcommon.so 2>/dev/null | grep "AddDescriptors\\|AddDescriptorsRunner" | head -5', "libcommon.so AddDescriptors 符号")
run('nm -D /lib64/libcommon.so 2>/dev/null | grep "FeatureReq\\|Device.*default_type\\|CtlReq" | head -10', "libcommon.so protobuf 生成符号")

# ===== 4. 检查 /Server/www/d/ 下的 CGI 程序 =====
run('ls -la /Server/www/d/ 2>/dev/null', "Server CGI 程序列表")

# ===== 5. 检查 /Agent/cmd/ 下的程序 =====
run('ls -la /Agent/cmd/ 2>/dev/null', "Agent cmd 程序列表")

# ===== 6. 检查 topn 是否存在 =====
run('find /Server -name "topn*" 2>/dev/null', "查找 topn 文件")

# ===== 7. 检查 threatinfo.cpp 中的 tisrs.conf 格式 =====
# 这个在本地代码库中查看

c.close()
print("\n诊断完成!")
