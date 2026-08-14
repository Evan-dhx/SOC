import paramiko
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 远程主机信息
HOST = '10.10.102.220'
USER = 'root'
PASS = 'PP@ssw0rd'

# 仓库中威胁情报数据文件 -> 远程部署路径的映射
TI_FILES = [
    # (本地路径, 远程路径, 描述)
    (r'd:\QorderProject\SOC\ly_analyser\ti\init\sus_threat',
     '/Agent/data/sus_threat',
     '可疑威胁IP列表 (SUS检测)'),
    (r'd:\QorderProject\SOC\ly_analyser\ti\init\ti_dns',
     '/Agent/data/ti_dns',
     '威胁DNS域名列表 (MD5哈希)'),
    (r'd:\QorderProject\SOC\ly_analyser\ti\init\mining_domain',
     '/Agent/data/mining_domain',
     '挖矿域名列表 (MD5哈希)'),
    (r'd:\QorderProject\SOC\ly_analyser\ti\init\mining_ip_bak',
     '/Agent/data/mining_ip',
     '挖矿IP列表'),
]

def check_remote_dir(ssh):
    """检查远程 /Agent/data/ 目录是否存在及其当前状态"""
    print("=" * 60)
    print("[1] 检查远程主机 /Agent/data/ 目录状态")
    print("=" * 60)

    stdin, stdout, stderr = ssh.exec_command(
        'ls -la /Agent/data/ 2>&1; echo "---EXIT:$?"'
    )
    out = stdout.read().decode('utf-8', errors='replace')
    print(out)

    # 检查是否已有威胁情报文件
    stdin, stdout, stderr = ssh.exec_command(
        'for f in sus_threat ti_dns mining_domain mining_ip mining_ip6; do '
        'if [ -f "/Agent/data/$f" ]; then '
        'echo "$f: $(wc -l < /Agent/data/$f) lines, $(du -h /Agent/data/$f | cut -f1)"; '
        'else echo "$f: NOT FOUND"; fi; done'
    )
    out = stdout.read().decode('utf-8', errors='replace')
    print("当前威胁情报文件状态:")
    print(out)

def upload_file(sftp, local_path, remote_path, desc):
    """通过 SFTP 上传单个文件"""
    local_size = os.path.getsize(local_path)
    print(f"\n  上传: {desc}")
    print(f"  本地: {local_path} ({local_size:,} bytes)")
    print(f"  远程: {remote_path}")

    start = time.time()
    sftp.put(local_path, remote_path)
    elapsed = time.time() - start

    # 验证远程文件大小
    remote_stat = sftp.stat(remote_path)
    remote_size = remote_stat.st_size

    status = "OK" if remote_size == local_size else "SIZE MISMATCH!"
    print(f"  远程文件大小: {remote_size:,} bytes [{status}]")
    print(f"  耗时: {elapsed:.1f}s")
    return remote_size == local_size

def verify_files(ssh):
    """验证所有文件部署成功"""
    print("\n" + "=" * 60)
    print("[6] 验证所有威胁情报文件部署结果")
    print("=" * 60)

    stdin, stdout, stderr = ssh.exec_command(
        'for f in sus_threat ti_dns mining_domain mining_ip; do '
        'if [ -f "/Agent/data/$f" ]; then '
        'echo "$f: $(wc -l < /Agent/data/$f) lines, $(du -h /Agent/data/$f | cut -f1)"; '
        'else echo "$f: NOT FOUND"; fi; done'
    )
    out = stdout.read().decode('utf-8', errors='replace')
    print(out)

    # 检查文件头部内容确认格式正确
    print("\n文件内容预览 (前3行):")
    for f in ['sus_threat', 'ti_dns', 'mining_domain', 'mining_ip']:
        stdin, stdout, stderr = ssh.exec_command(f'head -3 /Agent/data/{f} 2>&1')
        out = stdout.read().decode('utf-8', errors='replace')
        print(f"\n  /Agent/data/{f}:")
        for line in out.strip().split('\n'):
            print(f"    {line}")

def main():
    print("=" * 60)
    print("威胁情报数据部署脚本")
    print(f"目标主机: {HOST}")
    print("=" * 60)

    # 连接远程主机
    print(f"\n连接到 {HOST} ...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=30)
    print("连接成功!")

    # Step 1: 检查目录状态
    check_remote_dir(client)

    # Step 2-5: 上传文件
    print("\n" + "=" * 60)
    print("[2-5] 上传威胁情报数据文件到 /Agent/data/")
    print("=" * 60)

    sftp = client.open_sftp()

    all_ok = True
    for local_path, remote_path, desc in TI_FILES:
        if not os.path.exists(local_path):
            print(f"\n  [SKIP] 本地文件不存在: {local_path}")
            all_ok = False
            continue
        ok = upload_file(sftp, local_path, remote_path, desc)
        if not ok:
            all_ok = False

    sftp.close()

    # Step 6: 验证
    verify_files(client)

    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("所有威胁情报数据部署成功!")
    else:
        print("部分文件部署存在问题，请检查上面的输出。")
    print("=" * 60)

    client.close()

if __name__ == '__main__':
    main()
