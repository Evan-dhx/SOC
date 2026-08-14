import paramiko
import sys

def run_remote(cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    if out:
        print(out, end='')
    if err:
        print(err, end='', file=sys.stderr)
    sys.exit(exit_code)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ssh_exec.py <command>")
        sys.exit(1)
    run_remote(' '.join(sys.argv[1:]))
