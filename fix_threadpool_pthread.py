import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Create a pthread-based threadpool that avoids std::thread issues
print("=== Creating pthread-based threadpool.hpp ===")
fixed_code = r'''#pragma once

#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include <vector>
#include <queue>
#include <pthread.h>
#include <atomic>
#include <condition_variable>
#include <future>
#include <functional>
#include <stdexcept>
#include <memory>

namespace threadpool
{

class Threadpool
{
  private:
    struct ThreadData {
      Threadpool* pool;
      pthread_t thread_id;
    };
    
    std::vector<ThreadData*> pool;
    std::queue<std::function<void()> > tasks;
    pthread_mutex_t m_lock;
    pthread_cond_t cv_task;
    std::atomic<bool> stoped;
    std::atomic<int> idlThrNum;

    static void* worker_thread(void* arg)
    {
      ThreadData* data = static_cast<ThreadData*>(arg);
      Threadpool* self = data->pool;
      
      while(!self->stoped)
      {
        std::function<void()> task;
        {
          pthread_mutex_lock(&self->m_lock);
          while(!self->stoped && self->tasks.empty()) {
            pthread_cond_wait(&self->cv_task, &self->m_lock);
          }
          if (self->stoped && self->tasks.empty()) {
            pthread_mutex_unlock(&self->m_lock);
            return nullptr;
          }
          task = std::move(self->tasks.front());
          self->tasks.pop();
          pthread_mutex_unlock(&self->m_lock);
        }
        self->idlThrNum--;
        task();
        self->idlThrNum++;
      }
      return nullptr;
    }

  public:
    Threadpool(int pool_size) : stoped(false)
    {
      pthread_mutex_init(&m_lock, nullptr);
      pthread_cond_init(&cv_task, nullptr);
      idlThrNum = pool_size < 1 ? 1 : pool_size;
      for (int i = 0; i < idlThrNum; ++i)
      {
        ThreadData* data = new ThreadData{this, 0};
        pthread_create(&data->thread_id, nullptr, worker_thread, data);
        pool.push_back(data);
      }
    }

    ~Threadpool()
    {
      stoped.store(true);
      pthread_cond_broadcast(&cv_task);
      for (ThreadData* data : pool) {
        pthread_join(data->thread_id, nullptr);
        delete data;
      }
      pthread_mutex_destroy(&m_lock);
      pthread_cond_destroy(&cv_task);
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
        pthread_mutex_lock(&m_lock);
        tasks.emplace(
          [task]()
          {
            (*task)();
          });
        pthread_mutex_unlock(&m_lock);
      }
      pthread_cond_signal(&cv_task);
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
echo 'Written pthread-based threadpool.hpp'"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Also fix ly_analyser version
cmd_ly = f"""cat > /root/SOC/ly_analyser_src/common/threadpool.hpp << 'EOFMARKER'
{fixed_code}
EOFMARKER
echo 'Written ly_analyser pthread-based threadpool.hpp'"""
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
