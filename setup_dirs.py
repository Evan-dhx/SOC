import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

dirs = [
    '/Agent/cmd', '/Agent/lib', '/Agent/data', '/Agent/etc',
    '/Agent/tmp', '/Agent/log', '/Agent/cache',
    '/Server/bin', '/Server/www/d', '/Server/www/ui',
    '/Server/cmd', '/Server/lib', '/Server/etc',
    '/data/flow'
]

for d in dirs:
    stdin, stdout, stderr = client.exec_command(f'mkdir -p {d}')
    stdout.read()

stdin, stdout, stderr = client.exec_command('ls -d /Agent/bin /Agent/cmd /Agent/lib /Server/bin /Server/www /data/flow')
print(stdout.read().decode())

client.close()
