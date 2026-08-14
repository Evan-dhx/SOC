import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View extractor.cpp full logic", r"""
echo "=== extractor.cpp 完整代码 ==="
cat /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -200
"""),

    ("Fix crontab and launch script", r"""
echo "=== 1. 修复 crontab（去掉 root 用户名） ==="
crontab -l > /tmp/crontab.bak 2>/dev/null
cat > /tmp/new_crontab << 'EOF'
# LiuYing Agent scheduled tasks
# Run config_pusher every 5 minutes
*/5 * * * * /Server/bin/config_pusher >> /data/log/config_pusher.log 2>&1

# Run indexer process check every minute
* * * * * /Agent/bin/launch_indexer.sh >> /data/log/indexer.log 2>&1

# Clean old flow data daily at 2am
0 2 * * * find /data/flow -name "*.old" -delete >> /data/log/cleanup.log 2>&1
EOF
crontab /tmp/new_crontab
echo "crontab 已更新："
crontab -l
echo ""
echo "=== 2. 修复 launch_indexer.sh（cd /Agent/bin） ==="
cat > /Agent/bin/launch_indexer.sh << 'EOF'
#!/bin/bash

#set x

#sleep 12

cd /Agent/bin

now=`date +"%s"`

aligned_now=$[$now-$now%300-300]

echo $aligned_now



endtime=$[$aligned_now-3600*24]

#endtime=$[$aligned_now]

while [ $endtime -le $aligned_now ]

do

  #cmd="/Agent/bin/extractor -v 1 -t $endtime -n"
  cmd="sudo -u apache ./extractor -v 1 -t $endtime -i ./indexer"
  #cmd="sudo -u apache DEBUG=ALL ./extractor -v 1 -t $endtime -i ./indexer"
  echo $cmd
  $cmd 
  endtime=$[$endtime+300]

done
EOF
chmod +x /Agent/bin/launch_indexer.sh
echo "launch_indexer.sh 已更新"
echo ""
echo "=== 3. 手动测试 launch_indexer.sh（30 秒超时） ==="
timeout 30 /Agent/bin/launch_indexer.sh 2>&1 | head -10
echo "Exit: $?"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
