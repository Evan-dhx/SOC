import paramiko
import os
import sys

def upload_file(local_path, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
    sftp = client.open_sftp()
    
    file_size = os.path.getsize(local_path)
    print(f"Uploading {os.path.basename(local_path)} ({file_size / 1024 / 1024:.1f} MB)...")
    
    transferred = [0]
    def progress(sent, total):
        transferred[0] = sent
        pct = sent * 100 / total
        print(f"\r  Progress: {pct:.1f}%", end='', flush=True)
    
    sftp.put(local_path, remote_path, callback=progress)
    print(f"\n  Done: {remote_path}")
    
    sftp.close()
    client.close()

def upload_dir(local_dir, remote_dir):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
    sftp = client.open_sftp()
    
    def ensure_remote_dir(d):
        try:
            sftp.stat(d)
        except FileNotFoundError:
            ensure_remote_dir(os.path.dirname(d))
            sftp.mkdir(d)
    
    def walk_dir(local, remote):
        for item in os.listdir(local):
            local_path = os.path.join(local, item)
            remote_path = remote + '/' + item
            if os.path.isdir(local_path):
                if item in ['.git', '__pycache__', 'node_modules']:
                    continue
                ensure_remote_dir(remote_path)
                walk_dir(local_path, remote_path)
            else:
                file_size = os.path.getsize(local_path)
                print(f"  {remote_path} ({file_size / 1024:.1f} KB)")
                sftp.put(local_path, remote_path)
    
    ensure_remote_dir(remote_dir)
    walk_dir(local_dir, remote_dir)
    
    sftp.close()
    client.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python ssh_upload.py <local_path> <remote_path>")
        sys.exit(1)
    
    local_path = sys.argv[1]
    remote_path = sys.argv[2]
    
    if os.path.isdir(local_path):
        upload_dir(local_path, remote_path)
    else:
        upload_file(local_path, remote_path)
