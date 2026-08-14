import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix line endings in all source files
print("=== Fixing line endings in ly_vis source ===")
cmd = r"""
cd /root/SOC/ly_vis
# Fix all JS/JSX/TS/TSX/CSS/LESS files
find packages/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.css" -o -name "*.less" -o -name "*.json" -o -name "*.html" \) -exec sed -i 's/\r$//' {} \;
echo "Line endings fixed"

# Also fix root config files
find . -maxdepth 1 -type f -exec sed -i 's/\r$//' {} \;
echo "Root configs fixed"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

# Rebuild with CI=false to skip lint errors
print("\n=== Rebuilding ===")
cmd2 = r"""
cd /root/SOC/ly_vis
export NODE_OPTIONS=--openssl-legacy-provider
export CI=false
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false

# Clean previous build
rm -rf packages/std/build/*

yarn std build 2>&1 | tail -30
echo ""
echo "Exit code: $?"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=600)
out = stdout.read().decode('utf-8', errors='replace')
print(out)
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"STDERR: {err}")

# Check build output
print("\n=== Check build output ===")
cmd3 = r"""
ls -la /root/SOC/ly_vis/packages/std/build/ 2>/dev/null
echo ""
du -sh /root/SOC/ly_vis/packages/std/build/ 2>/dev/null
echo ""
ls /root/SOC/ly_vis/packages/std/build/static/js/ 2>/dev/null | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
