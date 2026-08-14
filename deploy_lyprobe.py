"""
将 ly_probe 流量探针上传到开发服务器并编译安装 (修复版)
目标服务器: 10.10.102.220
"""
import paramiko
import os
import tarfile
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 配置
SERVER_HOST = '10.10.102.220'
SERVER_USER = 'root'
SERVER_PASS = 'PP@ssw0rd'
LOCAL_DIR = r'D:\QorderProject\SOC\ly_probe'
REMOTE_DIR = '/root/ly_probe'
ARCHIVE_NAME = 'ly_probe.tar.gz'
ARCHIVE_PATH = os.path.join(r'D:\QorderProject\SOC', ARCHIVE_NAME)

def print_step(step, desc):
    print(f"\n[{step}] {desc}")
    print("-" * 50)

def create_archive():
    """打包本地 ly_probe 目录（排除 .deps 和旧编译文件）"""
    print_step(1, "打包 ly_probe 源码...")
    
    if os.path.exists(ARCHIVE_PATH):
        os.remove(ARCHIVE_PATH)
        print(f"  已删除旧压缩包: {ARCHIVE_PATH}")
    
    def exclude_filter(tarinfo):
        # 排除 .deps 目录和编译产物
        name = tarinfo.name
        if '/.deps' in name or name.endswith('/.deps'):
            return None
        if name.endswith('.o') or name.endswith('.lo') or name.endswith('.Po') or name.endswith('.Plo'):
            return None
        if '/.libs' in name or name.endswith('/.libs'):
            return None
        return tarinfo
    
    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(LOCAL_DIR, arcname="ly_probe", filter=exclude_filter)
    
    size_mb = os.path.getsize(ARCHIVE_PATH) / (1024 * 1024)
    print(f"  打包完成: {ARCHIVE_PATH}")
    print(f"  文件大小: {size_mb:.2f} MB")
    return ARCHIVE_PATH

def upload_archive(client, local_path, remote_path):
    """上传压缩包到服务器"""
    print_step(2, "上传到开发服务器...")
    
    sftp = client.open_sftp()
    print(f"  本地文件: {local_path}")
    print(f"  远程路径: {remote_path}")
    
    transferred = [0]
    last_print = [time.time()]
    
    def progress(sent, total):
        transferred[0] = sent
        now = time.time()
        if now - last_print[0] >= 1:
            pct = sent / total * 100
            print(f"\r  上传进度: {pct:.1f}%", end='', flush=True)
            last_print[0] = now
    
    sftp.put(local_path, remote_path, callback=progress)
    print(f"\r  上传完成: 100%")
    sftp.close()

def exec_remote(client, cmd, timeout=300):
    """执行远程命令并返回输出"""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return out, err, exit_code

def remote_install(client):
    """在远程服务器上解压并编译安装"""
    print_step(3, "远程解压...")
    
    cmd = f"rm -rf {REMOTE_DIR} && tar -xzf /root/{ARCHIVE_NAME} -C /root/"
    out, err, code = exec_remote(client, cmd)
    if code == 0:
        print(f"  解压完成: {REMOTE_DIR}")
    else:
        print(f"  解压失败: {err}")
        return False
    
    print_step(4, "检查编译依赖...")
    
    deps_check = """
    echo "GCC: $(gcc --version 2>/dev/null | head -1 || echo 'NOT FOUND')"
    echo "Make: $(make --version 2>/dev/null | head -1 || echo 'NOT FOUND')"
    echo "libpcap: $(pkg-config --modversion libpcap 2>/dev/null || echo 'checking...')"
    rpm -q libpcap-devel 2>/dev/null || echo "libpcap-devel: NOT INSTALLED"
    """
    out, _, _ = exec_remote(client, deps_check)
    print(out)
    
    print_step(5, "配置编译环境 (./configure)...")
    
    # 修复所有脚本文件的 Windows 换行符问题
    cmd = f"""cd {REMOTE_DIR} && \\
        for f in configure config.sub config.guess compile depcomp install-sh missing libtool ltmain.sh autogen.sh; do \\
            [ -f "$f" ] && sed -i 's/\\r$//' "$f"; \\
        done && \\
        chmod +x configure config.sub config.guess compile depcomp install-sh missing autogen.sh 2>/dev/null; \\
        ./configure --prefix=/usr/local 2>&1 | tail -30"""
    out, err, code = exec_remote(client, cmd, timeout=180)
    print(out)
    if code != 0:
        print(f"  configure 失败: {err}")
        return False
    print("  configure 完成")
    
    print_step(6, "编译 (make)...")
    
    # 确保 .deps 目录存在
    cmd = f"""cd {REMOTE_DIR} && \\
        mkdir -p .deps && \\
        make -j2 2>&1"""
    out, err, code = exec_remote(client, cmd, timeout=300)
    print(out[-3000:] if len(out) > 3000 else out)  # 只显示最后部分
    if code != 0:
        print(f"  make 失败: {err}")
        return False
    print("  编译完成")
    
    print_step(7, "安装 (make install)...")
    
    cmd = f"cd {REMOTE_DIR} && make install 2>&1"
    out, err, code = exec_remote(client, cmd, timeout=60)
    print(out)
    if code != 0:
        print(f"  make install 失败: {err}")
        return False
    
    print_step(8, "验证安装...")
    
    cmd = """
    echo "=== lyprobe 位置 ==="
    which lyprobe 2>/dev/null || echo "NOT IN PATH"
    ls -la /usr/local/bin/lyprobe 2>/dev/null || echo "binary not found at /usr/local/bin"
    
    echo ""
    echo "=== lyprobe 帮助 ==="
    lyprobe --help 2>&1 | head -10 || /usr/local/bin/lyprobe --help 2>&1 | head -10 || echo "help not available"
    """
    out, _, _ = exec_remote(client, cmd)
    print(out)
    
    return True

def main():
    print("=" * 60)
    print("ly_probe 流量探针部署工具 (修复版)")
    print("=" * 60)
    print(f"目标服务器: {SERVER_HOST}")
    print(f"本地源码: {LOCAL_DIR}")
    
    if not os.path.isdir(LOCAL_DIR):
        print(f"\n错误: 本地目录不存在: {LOCAL_DIR}")
        return
    
    # 1. 打包（排除 .deps）
    archive_path = create_archive()
    
    # 2. 连接服务器
    print_step(2, "连接开发服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASS, timeout=30)
        print(f"  连接成功: {SERVER_USER}@{SERVER_HOST}")
    except Exception as e:
        print(f"  连接失败: {e}")
        return
    
    try:
        # 3. 上传
        remote_archive = f"/root/{ARCHIVE_NAME}"
        upload_archive(client, archive_path, remote_archive)
        
        # 4-8. 远程编译安装
        success = remote_install(client)
        
        print("\n" + "=" * 60)
        if success:
            print("部署完成!")
            print("=" * 60)
            print("\nlyprobe 已安装到 /usr/local/bin/lyprobe")
            print("\n使用示例:")
            print("  lyprobe -i eth0 -n 127.0.0.1:9995 -e 0 -w 32768 -G")
        else:
            print("部署过程中出现错误，请检查日志")
            print("=" * 60)
    
    finally:
        client.close()
    
    # 清理本地压缩包
    if os.path.exists(ARCHIVE_PATH):
        os.remove(ARCHIVE_PATH)
        print(f"\n已清理本地临时文件: {ARCHIVE_PATH}")

if __name__ == '__main__':
    main()
