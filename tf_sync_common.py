import paramiko
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCAL_DIR = r'd:\QorderProject\SOC\ly_analyser\src\common'
REMOTE_DIR = '/root/SOC/ly_analyser_src/common'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 获取远程文件列表
stdin, stdout, stderr = client.exec_command(f'ls {REMOTE_DIR}')
remote_files = set(stdout.read().decode().split())

sftp = client.open_sftp()
missing = []
for f in os.listdir(LOCAL_DIR):
    if f.endswith(('.h', '.cpp', '.hpp', '.proto')) and f not in remote_files:
        missing.append(f)
        sftp.put(os.path.join(LOCAL_DIR, f), f'{REMOTE_DIR}/{f}')
sftp.close()
print("缺失并已同步的文件:", missing if missing else "无")

client.close()