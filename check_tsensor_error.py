"""
正確重新編譯 liblyprobe-1.0.0.so 並修復 FPE 崩潰
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("正確重新編譯 liblyprobe-1.0.0.so")
print("=" * 60)

# 步驟1: 停止服務
print("\n[1] 停止服務...")
stdin, stdout, stderr = client.exec_command("systemctl stop tsensor.service; pkill tsensor 2>/dev/null; sleep 1", timeout=15)
stdout.read()
print("  已停止")

# 步驟2: 用 -fPIC 重新編譯所有庫的 .o 文件到 .libs/
print("[2] 用 -fPIC 重新編譯所有庫源文件...")
stdin, stdout, stderr = client.exec_command("""
cd /root/tsensor
mkdir -p .libs

# 庫需要的源文件列表
SRCS="base64.c collect.c database.c engine.c export.c fb.c globals.c plugin.c sflow_collect.c util.c version.c"

for src in $SRCS; do
    obj=$(echo $src | sed 's/\\.c$/.o/')
    echo "  編譯 $src → .libs/$obj"
    gcc -DHAVE_CONFIG_H -I. -I. -I/usr/include/mysql -I/usr/include/mysql/mysql \
        -I/usr/local/include -I/opt/local/include \
        -g -O2 -pipe -fPIC \
        -c -o .libs/$obj $src 2>&1 | grep -i error || true
done

echo ""
echo "=== .libs/ 中的 .o 文件 ==="
ls -la .libs/*.o 2>/dev/null | wc -l
echo "個文件"
""", timeout=60)
out = stdout.read().decode('utf-8', errors='replace')
print(out)

# 步驟3: 鏈接共享庫
print("[3] 鏈接 liblyprobe-1.0.0.so...")
stdin, stdout, stderr = client.exec_command("""
cd /root/tsensor
gcc -shared -o .libs/liblyprobe-1.0.0.so \
    .libs/base64.o .libs/collect.o .libs/database.o .libs/engine.o \
    .libs/export.o .libs/fb.o .libs/globals.o .libs/plugin.o \
    .libs/sflow_collect.o .libs/util.o .libs/version.o \
    -lpcre -lresolv -ldl -lpthread -lmariadb -lpcap 2>&1

if [ -f .libs/liblyprobe-1.0.0.so ]; then
    echo "✓ 成功: $(ls -la .libs/liblyprobe-1.0.0.so | awk '{print $5}') bytes"
    
    # 安裝
    cp .libs/liblyprobe-1.0.0.so /usr/local/lib/liblyprobe-1.0.0.so
    chmod 755 /usr/local/lib/liblyprobe-1.0.0.so
    ldconfig
    echo "✓ 已安裝到 /usr/local/lib/"
else
    echo "✗ 編譯失敗"
fi
""", timeout=30)
print(stdout.read().decode().strip())

# 步驟4: 重新鏈接 tsensor 二進制
print("[4] 重新鏈接 tsensor 二進制...")
stdin, stdout, stderr = client.exec_command("""
cd /root/tsensor
gcc -o lyprobe lyprobe-nprobe.o -L/usr/local/lib -llyprobe -lpcre -lresolv -lm -lmariadb -lpcap 2>&1

if [ -f lyprobe ]; then
    echo "✓ tsensor: $(ls -la lyprobe | awk '{print $5}') bytes"
    cp lyprobe /usr/local/bin/tsensor
    echo "✓ 已安裝"
else
    echo "✗ 失敗"
fi
""", timeout=30)
print(stdout.read().decode().strip())

# 步驟5: 驗證符號大小一致
print("[5] 驗證符號大小一致性...")
stdin, stdout, stderr = client.exec_command("""
echo "=== 二進制中的 readOnlyGlobals ==="
nm /usr/local/bin/tsensor | grep readOnlyGlobals

echo ""
echo "=== 庫中的 readOnlyGlobals ==="
nm -D /usr/local/lib/liblyprobe-1.0.0.so | grep readOnlyGlobals

echo ""
echo "=== 檢查 TEMPLATE_LIST_LEN ==="
strings /usr/local/lib/liblyprobe-1.0.0.so | grep -i template | head -5 || echo "(無直接字符串)"

echo ""
echo "=== ldd 檢查 ==="
ldd /usr/local/bin/tsensor | grep lyprobe
""", timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟6: 重新編譯 l7Plugin 和 servicePlugin (添加 dirent.h)
print("[6] 修復 l7Plugin 和 servicePlugin 的 dirent.h 問題...")
stdin, stdout, stderr = client.exec_command("""
cd /root/tsensor/plugins

# 修復 l7Plugin.c
if ! grep -q "dirent.h" l7Plugin.c; then
    sed -i '1i #include <dirent.h>\\n#include <dlfcn.h>' l7Plugin.c
    echo "  l7Plugin.c: 已添加 dirent.h"
fi

# 修復 servicePlugin.c
if ! grep -q "dirent.h" servicePlugin.c; then
    sed -i '1i #include <dirent.h>\\n#include <dlfcn.h>' servicePlugin.c
    echo "  servicePlugin.c: 已添加 dirent.h"
fi

# 重新編譯這兩個插件
echo ""
echo "重新編譯 l7Plugin..."
gcc -shared -fPIC -O2 -DHAVE_CONFIG_H -I.. -I/usr/local/include \
    -o /usr/local/lib/tsensor/plugins/l7Plugin.so l7Plugin.c cJSON.c 2>&1 | grep -i error || echo "  ✓ l7Plugin.so"

echo "重新編譯 servicePlugin..."
gcc -shared -fPIC -O2 -DHAVE_CONFIG_H -DHAVE_PCRE_H -DHAVE_LIBPCRE -I.. -I/usr/local/include \
    -o /usr/local/lib/tsensor/plugins/servicePlugin.so servicePlugin.c cJSON.c -lpcre 2>&1 | grep -i error || echo "  ✓ servicePlugin.so"
""", timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟7: 啟動服務
print("[7] 啟動服務...")
stdin, stdout, stderr = client.exec_command("""
systemctl start tsensor.service
sleep 5
systemctl is-active tsensor.service
""", timeout=20)
status = stdout.read().decode().strip()
print(f"  狀態: {status}")

# 步驟8: 檢查日誌
print("[8] 檢查日誌...")
stdin, stdout, stderr = client.exec_command("""
echo "=== 最新日誌 ==="
journalctl -u tsensor --no-pager -n 20

echo ""
echo "=== 關鍵檢查 ==="
journalctl -u tsensor --no-pager -n 20 | grep "different size" && echo "  ✗ 符號不匹配" || echo "  ✓ 無符號警告"
journalctl -u tsensor --no-pager -n 20 | grep "too many" && echo "  ✗ too many 錯誤" || echo "  ✓ 無 too many"
journalctl -u tsensor --no-pager -n 20 | grep "Unable to add further" && echo "  ✗ 模板上限不足" || echo "  ✓ 模板上限OK"
journalctl -u tsensor --no-pager -n 20 | grep "plugin(s) enabled"
""", timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟9: 等待 65 秒確認穩定
print("[9] 等待 65 秒確認穩定...")
stdin, stdout, stderr = client.exec_command("""
sleep 65
echo "=== 65 秒後 ==="
systemctl is-active tsensor.service
echo ""
echo "=== 崩潰檢查 ==="
journalctl -u tsensor --no-pager --since "70 seconds ago" | grep -E 'SEGV|FPE|core-dump' || echo "  無崩潰! ✓"
echo ""
echo "=== 關鍵錯誤 ==="
journalctl -u tsensor --no-pager --since "70 seconds ago" | grep -E 'too many|Unable to add|different size' || echo "  無關鍵錯誤! ✓"
echo ""
echo "=== 進程 ==="
ps -ef | grep tsensor | grep -v grep
""", timeout=90)
out = stdout.read().decode('utf-8', errors='replace')
print(out)

client.close()

print("\n" + "=" * 60)
if "active" in out and "無崩潰" in out:
    print("修復成功！tsensor 穩定運行")
elif "active" in out:
    print("服務運行中，但仍有問題需檢查")
else:
    print("服務未穩定，請檢查日誌")
print("=" * 60)
