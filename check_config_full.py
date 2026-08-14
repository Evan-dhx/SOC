import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 查看完整配置文件，搜索 policy_index / sus / black / mining / storage 等关键字
stdin, stdout, stderr = c.exec_command(
    'cat /Agent/data/config 2>/dev/null'
)
config = stdout.read().decode('utf-8', errors='replace')
print('=== Agent 配置文件 (完整) ===')
print(config)

# 搜索 policy_index 相关配置
print('\n=== 搜索 policy_index / sus / black / storage ===')
for line in config.split('\n'):
    lower = line.lower()
    if any(k in lower for k in ['policy_index', 'sus', 'black', 'white', 'mining', 'storage', 'pop_service', 'ip_set', 'bw']):
        print(f'  {line.strip()}')

c.close()
