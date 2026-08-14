# -*- coding: utf-8 -*-
"""上传更新后的 index.html 并验证列宽配置已生效。"""
import paramiko
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("10.10.102.220", username="root", password="PP@ssw0rd", timeout=30)

sftp = client.open_sftp()
sftp.put(r"d:\QorderProject\SOC\ti_server\static\index.html", "/opt/ti_server/static/index.html")
sftp.close()
print("== 已上传 index.html ==")

cmd = (
    "curl -sk https://127.0.0.1:8090/ "
    "| grep -o 'width:[0-9]*px' | sort | uniq -c"
)
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode("utf-8", errors="replace"))
client.close()
