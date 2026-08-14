import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the actual std_thread.h code around line 145
print("=== std_thread.h lines 130-150 ===")
cmd = r"""sed -n '130,150p' /usr/include/c++/11/bits/std_thread.h"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check if there's a macro conflict
print("\n=== Checking for 'size' macro conflicts ===")
cmd2 = r"""grep -n '#define size\|#define stoped\|#define pool' /root/SOC/ly_server_src/common/*.h 2>/dev/null | head -20"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Try a minimal test
print("\n=== Creating minimal threadpool test ===")
test_code = r'''#include <thread>
#include <vector>
#include <iostream>

class TestPool {
private:
    std::vector<std::thread> pool;
    bool stoped = false;
    
    void worker() {
        while(!stoped) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }
    
public:
    TestPool(int n) {
        for(int i = 0; i < n; i++) {
            pool.emplace_back(&TestPool::worker, this);
        }
    }
    
    ~TestPool() {
        stoped = true;
        for(auto& t : pool) t.join();
    }
};

int main() {
    TestPool p(4);
    std::cout << "OK" << std::endl;
    return 0;
}
'''

cmd3 = f"""cat > /tmp/test_thread.cpp << 'EOF'
{test_code}
EOF
g++ -std=c++11 -pthread /tmp/test_thread.cpp -o /tmp/test_thread 2>&1 && echo 'Compilation OK' || echo 'Compilation FAILED'"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
