import paramiko
import os

# First, check local ly_vis structure
local_ly_vis = r"d:\QorderProject\SOC\ly_vis"
print(f"=== Local ly_vis exists: {os.path.exists(local_ly_vis)} ===")
if os.path.exists(local_ly_vis):
    for f in os.listdir(local_ly_vis):
        print(f"  {f}")

# Connect to server
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Install Node.js 18 LTS
print("\n=== Step 1: Installing Node.js ===")
cmd = r"""
# Install Node.js 18 LTS via NodeSource
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash - 2>&1 | tail -5
yum install -y nodejs 2>&1 | tail -5
node --version
npm --version
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Step 2: Install yarn
print("\n=== Step 2: Installing Yarn ===")
cmd2 = r"""
npm install -g yarn 2>&1 | tail -5
yarn --version
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=60)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# Step 3: Upload ly_vis via SFTP
print("\n=== Step 3: Uploading ly_vis ===")
sftp = client.open_sftp()

def upload_dir(local_dir, remote_dir):
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
    
    count = 0
    for item in os.listdir(local_dir):
        if item in ['node_modules', '.git', 'dist']:
            continue
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item
        if os.path.isdir(local_path):
            count += upload_dir(local_path, remote_path)
        else:
            try:
                sftp.put(local_path, remote_path)
                count += 1
            except Exception as e:
                print(f"  Skip {item}: {e}")
    return count

if os.path.exists(local_ly_vis):
    remote_base = "/root/SOC/ly_vis"
    count = upload_dir(local_ly_vis, remote_base)
    print(f"Uploaded {count} files to {remote_base}")
else:
    print("ly_vis not found locally, checking if already on server...")
    stdin, stdout, stderr = client.exec_command("ls /root/SOC/ly_vis/ 2>/dev/null | head -10", timeout=10)
    print(stdout.read().decode())

sftp.close()

# Step 4: Build ly_vis
print("\n=== Step 4: Building ly_vis ===")
cmd4 = r"""
cd /root/SOC/ly_vis
ls -la
echo ""
cat package.json 2>/dev/null | head -20
echo ""
echo "=== Installing dependencies ==="
yarn install --network-timeout 100000 2>&1 | tail -20
echo ""
echo "=== Building ==="
yarn build 2>&1 | tail -20 || npm run build 2>&1 | tail -20 || lerna run build 2>&1 | tail -20
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
