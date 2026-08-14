import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Create a fixed version of threadpool.hpp
print("=== Creating fixed threadpool.hpp ===")
fixed_code = r'''#pragma once

#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include <vector>
#include <queue>
#include <thread>
#include <atomic>
#include <condition_variable>
#include <future>
#include <functional>
#include <stdexcept>

namespace threadpool
{

class Threadpool
{
  private:
    std::vector<std::thread> pool;
    std::queue<std::function<void()> > tasks;
    std::mutex m_lock;
    std::condition_variable cv_task;
    std::atomic<bool> stoped;
    std::atomic<int>  idlThrNum;

    void worker_thread()
    {
      while(!stoped)
      {
        std::function<void()> task;
        {
          std::unique_lock<std::mutex> lock{ m_lock };
          cv_task.wait(lock,
            [this] {
                return stoped.load() || !tasks.empty();
            }
          );
          if (stoped && tasks.empty())
            return;
          task = std::move(tasks.front());
          tasks.pop();
        }
        idlThrNum--;
        task();
        idlThrNum++;
      }
    }

  public:
    Threadpool(int pool_size) : stoped(false)
    {
      idlThrNum = pool_size < 1 ? 1 : pool_size;
      for (int i = 0; i < idlThrNum; ++i)
      {
        pool.emplace_back(&Threadpool::worker_thread, this);
      }
    }

    ~Threadpool()
    {
      stoped.store(true);
      cv_task.notify_all();
      for (std::thread& thread : pool) {
        if(thread.joinable())
          thread.join();
      }
    }

    template<class F, class... Args>
    auto commit(F&& f, Args&&... args) ->std::future<decltype(f(args...))>
    {
      if (stoped.load())
        throw std::runtime_error("commit on ThreadPool is stopped.");

      using RetType = decltype(f(args...));
      auto task = std::make_shared<std::packaged_task<RetType()> >(
        std::bind(std::forward<F>(f), std::forward<Args>(args)...));
      std::future<RetType> future = task->get_future();
      {
        std::lock_guard<std::mutex> lock{ m_lock };
        tasks.emplace(
          [task]()
          {
            (*task)();
          });
      }
      cv_task.notify_one();
      return future;
    }

    int idlCount() { return idlThrNum; }
};

}

#endif
'''

# Write the fixed code
cmd = f"""cat > /root/SOC/ly_server_src/common/threadpool.hpp << 'EOFMARKER'
{fixed_code}
EOFMARKER
echo 'Written threadpool.hpp'"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Also fix ly_analyser version
cmd_ly = f"""cat > /root/SOC/ly_analyser_src/common/threadpool.hpp << 'EOFMARKER'
{fixed_code}
EOFMARKER
echo 'Written ly_analyser threadpool.hpp'"""
stdin, stdout, stderr = client.exec_command(cmd_ly, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Recompile server
print("\n=== Recompiling server module ===")
cmd2 = r"""cd /root/SOC/ly_server_src/server && make clean 2>&1 | tail -2 && make -j4 2>&1 | tail -80"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
