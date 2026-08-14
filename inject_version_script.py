import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=30):
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:5000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("通过 SFTP 注入版本号移动脚本")
print("=" * 70)

# ---- 1. 读取当前 index.html ----
print("\n--- [1] 读取 index.html ---")
sftp = c.open_sftp()
with sftp.file('/Server/www/ui/index.html', 'r') as f:
    html = f.read().decode('utf-8')
print(f"文件长度: {len(html)} 字符")
print(f"包含 moveVersion: {'moveVersion' in html}")

# ---- 2. 在 </body> 前注入 JavaScript ----
print("\n--- [2] 注入 JavaScript ---")

inject_js = """<script>
(function(){
  function moveVersion(){
    var vt=document.querySelector('.version-text');
    if(!vt){setTimeout(moveVersion,200);return;}
    var btn=document.querySelector('.login-form .ant-btn-primary')||document.querySelector('button[type=submit]');
    if(btn&&btn.parentNode){
      if(vt.parentNode!==btn.parentNode){
        btn.parentNode.appendChild(vt);
        vt.style.textAlign='center';
        vt.style.marginTop='15px';
        vt.style.color='#666';
        vt.style.fontSize='12px';
      }
    }else{
      setTimeout(moveVersion,200);
    }
  }
  if(document.readyState==='complete'){moveVersion();}
  else{window.addEventListener('load',function(){setTimeout(moveVersion,500);});}
  var observer=new MutationObserver(function(){
    var vt=document.querySelector('.version-text');
    var btn=document.querySelector('.login-form .ant-btn-primary')||document.querySelector('button[type=submit]');
    if(vt&&btn&&vt.parentNode!==btn.parentNode){
      btn.parentNode.appendChild(vt);
      vt.style.textAlign='center';
      vt.style.marginTop='15px';
      vt.style.color='#666';
      vt.style.fontSize='12px';
    }
  });
  observer.observe(document.body,{childList:true,subtree:true});
})();
</script>"""

if 'moveVersion' not in html:
    html = html.replace('</body>', inject_js + '</body>')
    with sftp.file('/Server/www/ui/index.html', 'w') as f:
        f.write(html)
    print("注入成功!")
else:
    print("已存在，跳过注入")

sftp.close()

# ---- 3. 验证注入 ----
print("\n--- [3] 验证注入 ---")
run('grep -c "moveVersion" /Server/www/ui/index.html', "moveVersion 计数")
run('tail -3 /Server/www/ui/index.html | head -2', "index.html 末尾")

# ---- 4. 解锁 admin ----
print("\n--- [4] 解锁 admin ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0;" server 2>/dev/null', "解锁")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")

# ---- 5. 重启 httpd 并测试 ----
print("\n--- [5] 重启 httpd 并测试 ---")
run('systemctl restart httpd 2>&1', "重启")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ 2>&1', "首页状态")
run('curl -s http://127.0.0.1/ 2>&1 | grep -o "moveVersion" | wc -l', "页面中 moveVersion 计数")
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin 登录测试")

c.close()
print("\n" + "=" * 70)
print("注入完成!")
print("=" * 70)
