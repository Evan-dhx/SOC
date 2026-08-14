import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

client.exec_command('mkdir -p /root/nftls_build && sleep 1')[1].read()
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\nftls\nftls.c', '/root/nftls_build/nftls.c')
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\nftls\Makefile', '/root/nftls_build/Makefile')
sftp.close()
print("源码已上传")

cmds = [
    ("编译 nftls", r"""
cd /root/nftls_build
make 2>&1
ls -la nftls
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()