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
print("通过 JS 注入移动版本号位置")
print("=" * 70)

# ---- 1. 在 index.html 中注入 JavaScript ----
print("\n--- [1] 注入版本号移动脚本 ---")

# 读取当前 index.html
run('cat /Server/www/ui/index.html', "当前 index.html")

# 在 </body> 前插入一段 JavaScript
# 这段脚本会在页面加载后：
# 1. 找到 .version-text 元素
# 2. 找到登录按钮（.ant-btn-primary 或 form 中的 button）
# 3. 将 version-text 移到登录按钮后面
inject_js = """<script>
(function(){
  function moveVersion(){
    var vt=document.querySelector('.version-text');
    if(!vt){setTimeout(moveVersion,200);return;}
    // 找到登录表单中的提交按钮
    var btn=document.querySelector('.login-form .ant-btn-primary')||document.querySelector('button[type=submit]');
    if(btn&&btn.parentNode){
      // 如果 version-text 的父节点不是按钮的父节点，则移动
      if(vt.parentNode!==btn.parentNode){
        btn.parentNode.appendChild(vt);
        vt.style.textAlign='center';
        vt.style.marginTop='15px';
        vt.style.color='#666';
        vt.style.fontSize='12px';
      }
    }else{
      // 如果按钮还没加载，等待
      setTimeout(moveVersion,200);
    }
  }
  // 页面加载后执行
  if(document.readyState==='complete'){
    moveVersion();
  }else{
    window.addEventListener('load',function(){setTimeout(moveVersion,500);});
  }
  // MutationObserver 监听 DOM 变化（React 重新渲染时重新移动）
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

# 用 python3 在远程执行替换
sftp = c.open_sftp()
with sftp.file('/tmp/inject_script.txt', 'w') as f:
    f.write(inject_js)
sftp.close()

# 在 </body> 前插入脚本
run("python3 -c \""
     "with open('/Server/www/ui/index.html','r') as f: s=f.read();"
     "with open('/tmp/inject_script.txt','r') as f: js=f.read();"
     "if 'moveVersion' not in s:"
     "  s=s.replace('</body>', js+'</body>');"
     "  with open('/Server/www/ui/index.html','w') as f: f.write(s);"
     "  print('INJECTED');"
     "else:"
     "  print('ALREADY INJECTED');"
     "\"", "注入脚本", timeout=15)

# ---- 2. 验证注入 ----
print("\n--- [2] 验证注入 ---")
run('grep -c "moveVersion" /Server/www/ui/index.html', "moveVersion 存在计数")
run('grep -o "moveVersion" /Server/www/ui/index.html | wc -l', "moveVersion 出现次数")
run('tail -5 /Server/www/ui/index.html', "index.html 末尾")

# ---- 3. 解锁 admin ----
print("\n--- [3] 解锁 admin ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0;" server 2>/dev/null', "解锁")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")

# ---- 4. 重启 httpd ----
print("\n--- [4] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ 2>&1', "首页状态")
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin 登录测试")

c.close()
print("\n" + "=" * 70)
print("修改完成!")
print("=" * 70)
