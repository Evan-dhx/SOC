import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

THREATCONF_CPP = r'''
#include "../../ly_analyser_src/common/common.h"
#include "../../ly_analyser_src/common/log.h"
#include "../../ly_analyser_src/common/ini.h"
#include "define.h"
#include <Cgicc.h>
#include <sstream>
#include <fstream>
#include <curl/curl.h>

using namespace std;
using namespace cgicc;

static size_t write_cb(void *ptr, size_t size, size_t nmemb, void *stream){
	((ostream*)stream)->write((const char*)ptr, size*nmemb);
	return size*nmemb;
}

static string esc(const string& s){
	string r;
	for (size_t i=0;i<s.size();i++){
		if (s[i]=='"' || s[i]=='\\') r+='\\';
		r+=s[i];
	}
	return r;
}

int main(){
	printf("Content-Type: application/javascript; charset=utf-8\r\n\r\n");
	Cgicc cgi;
	string op = cgi("op");
	Ini ini;

	if (op=="get"){
		ini.LoadFromFile(TIC_CONF);
		string api_key = ini.Get("API_KEY","");
		string tic_host = ini.Get("HOST","");
		string tic_port = ini.Get("PORT","");
		ini.LoadFromFile(TISRS_CONF);
		string key = ini.Get("KEY","");
		string tisrs_host = ini.Get("HOST","");
		string tisrs_port = ini.Get("PORT","");
		cout << "[{\"api_key\":\""<<esc(api_key)<<"\",\"key\":\""<<esc(key)
		     <<"\",\"tic_host\":\""<<esc(tic_host)<<"\",\"tic_port\":\""<<esc(tic_port)
		     <<"\",\"tisrs_host\":\""<<esc(tisrs_host)<<"\",\"tisrs_port\":\""<<esc(tisrs_port)<<"\"}]";
	}
	else if (op=="save"){
		ofstream f1(TIC_CONF);
		if (!f1){ cout<<"[{\"code\":500,\"msg\":\"无法写入 tic.conf\"}]"; return 0; }
		f1 << "API_KEY=" << cgi("api_key") << "\n"
		   << "HOST=" << cgi("tic_host") << "\n"
		   << "PORT=" << cgi("tic_port") << "\n";
		f1.close();
		ofstream f2(TISRS_CONF);
		if (!f2){ cout<<"[{\"code\":500,\"msg\":\"无法写入 tisrs.conf\"}]"; return 0; }
		f2 << "KEY=" << cgi("key") << "\n"
		   << "HOST=" << cgi("tisrs_host") << "\n"
		   << "PORT=" << cgi("tisrs_port") << "\n";
		f2.close();
		cout << "[{\"code\":200,\"msg\":\"保存成功\"}]";
	}
	else if (op=="test"){
		ini.LoadFromFile(TISRS_CONF);
		string key = ini.Get("KEY","");
		string host = ini.Get("HOST","");
		string port = ini.Get("PORT","");
		if (key.empty() || host.empty() || port.empty()){
			cout << "[{\"code\":400,\"msg\":\"威胁情报服务未配置\"}]";
			return 0;
		}
		string url = "http://" + host + ":" + port + "/apisix/plugin/jwt/sign?key=" + key;
		CURL *curl = curl_easy_init();
		if (!curl){ cout<<"[{\"code\":500,\"msg\":\"curl 初始化失败\"}]"; return 0; }
		ostringstream os;
		string postdata = "key=" + key;
		curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
		curl_easy_setopt(curl, CURLOPT_POST, 1L);
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postdata.c_str());
		curl_easy_setopt(curl, CURLOPT_TIMEOUT, 8L);
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_cb);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, &os);
		CURLcode res = curl_easy_perform(curl);
		long code = 0;
		if (res==CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
		curl_easy_cleanup(curl);
		if (res!=CURLE_OK)
			cout << "[{\"code\":500,\"msg\":\"连接失败:" << curl_easy_strerror(res) << "\"}]";
		else if (code==200)
			cout << "[{\"code\":200,\"msg\":\"连通正常，JWT 获取成功\"}]";
		else
			cout << "[{\"code\":" << code << ",\"msg\":\"服务返回 " << code << "，key 可能无效\"}]";
	}
	else {
		cout << "[{\"code\":400,\"msg\":\"无效操作\"}]";
	}
	return 0;
}
'''

cmds = [
    ("创建 threatconf.cpp + 编译部署", f"""
echo "=== 1. /Server/etc 当前权限 ==="
ls -la /Server/etc/ 2>&1
echo ""
echo "=== 2. 写入 threatconf.cpp ==="
cat > /root/SOC/ly_server_src/server/threatconf.cpp <<'CPPEOF'
{THREATCONF_CPP}
CPPEOF
echo "已写入"
echo ""
echo "=== 3. 编译 ==="
cd /root/SOC/ly_server_src/server
g++ threatconf.cpp dbc.o -Wall -g -std=c++17 -fpermissive -lpthread -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o threatconf 2>&1 | head -8
echo "编译退出码: $?"
ls -la threatconf 2>/dev/null
echo ""
echo "=== 4. 部署 + 权限 ==="
cp threatconf /Server/www/d/threatconf
chmod 755 /Server/www/d/threatconf
echo "已部署"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()