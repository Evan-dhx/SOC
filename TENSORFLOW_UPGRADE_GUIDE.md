# TensorFlow 2.12 升级指南

## 概述

将流影 SOC 平台的 TensorFlow 从 2.0.4（旧 ABI）升级到 2.12（兼容 GCC 11 new ABI），以启用 AI 过滤器功能。

## 背景

- **问题**: TF 2.0.4 使用旧版 C++ ABI 编译，与 AlmaLinux 9 的 GCC 11（默认 new ABI）不兼容
- **影响**: AI 过滤器（DGA、DNS隧道、恶意URL、挖矿）被禁用
- **解决方案**: 从源码编译 TF 2.12，自动使用 GCC 11 的 new ABI

## 升级步骤

### 阶段 1: 环境检查（已完成）

```bash
python tf_upgrade_phase1.py
```

检查结果：
- AlmaLinux 9.8 + GCC 11.5.0 ✓
- 15GB 内存（需添加 swap）
- 481GB 磁盘空间 ✓
- 4 核 CPU ✓

### 阶段 2: 编译 TensorFlow 2.12

```bash
# 建议在 screen 或 tmux 中运行
screen -S tf_build
python tf_upgrade_phase2.py
# 按 Ctrl+A+D 分离会话
```

此阶段会：
1. 添加 8GB swap 文件
2. 安装 Bazel 5.3.0
3. 下载 TF 2.12 源码（约 600MB）
4. 配置编译选项（CPU-only）
5. 启动后台编译（4-8 小时）

**监控进度**:
```bash
python tf_build_monitor.py
# 或直接查看日志
tail -f /tmp/tf_build.log
```

### 阶段 3: 安装与重新编译

```bash
# 等待编译完成后运行
python tf_upgrade_phase3.py
```

此阶段会：
1. 备份旧 TF 2.0.4 库
2. 安装 TF 2.12 库文件和头文件
3. 更新 Makefile include 路径
4. 重新编译 flow_filter.a（包含 AI 过滤器）
5. 重新编译并部署 indexer
6. 验证 AI 过滤器已启用

## 主要变更

### 1. 库文件路径

**旧版本（TF 2.0.4）**:
```
/usr/local/lib/libtensorflow_cc.so.2.0.4
/usr/local/lib/libtensorflow_framework.so.2.0.4
```

**新版本（TF 2.12）**:
```
/usr/local/lib/libtensorflow_cc.so.2.12.0
/usr/local/lib/libtensorflow_framework.so.2.12.0
```

### 2. 头文件路径

**旧版本**:
```
/usr/local/include/tf/tensorflow/
/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen/
/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl/
/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include/
/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto/
```

**新版本**:
```
/usr/local/include/tf/tensorflow/
/usr/local/include/tf/third_party/
/usr/local/include/tf/tensorflow/core/protobuf/  # bazel 生成的 proto 头文件
```

### 3. Makefile 变更

**flow/Makefile** 和 **indexing/Makefile** 的 INCS 路径更新：

```makefile
# 旧版本
INCS=-I. -I/usr/include -I/usr/local/include \
     -I/usr/local/include/tf/ \
     -I/usr/local/include/tf/bazel-genfiles \
     -I/usr/local/include/tf/tensorflow \
     -I/usr/local/include/tf/tensorflow/third-party \
     -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen \
     -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl \
     -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include \
     -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto

# 新版本
INCS=-I. -I/usr/include -I/usr/local/include \
     -I/usr/local/include/tf \
     -I/usr/local/include/tf/tensorflow \
     -I/usr/local/include/tf/third_party \
     -I/usr/local/include/tf/tensorflow/core/protobuf
```

### 4. C++ 标准

从 `-std=c++11` 升级到 `-std=c++14`（TF 2.12 要求）

## API 兼容性

代码中使用的 TensorFlow C++ API 在 2.12 中完全兼容：

| API | 状态 |
|-----|------|
| `tensorflow::NewSession(SessionOptions())` | ✓ 兼容 |
| `session->Run(inputs, outputs, &result)` | ✓ 兼容 |
| `tensorflow::Tensor(DT_INT32, TensorShape)` | ✓ 兼容 |
| `ReadBinaryProto(Env::Default(), path, &graph)` | ✓ 兼容 |
| `tensorflow::GraphDef` | ✓ 兼容 |
| 头文件路径 `tensorflow/cc/client/client_session.h` | ✓ 兼容 |

## 受影响的组件

### AI 过滤器（已启用）

1. **DGA 检测** (`dga_filter.cpp`)
   - 检测域名生成算法
   - 模型: `/Agent/data/models/dga_model.pb`

2. **DNS 隧道检测** (`dnstun_ai_filter.cpp`)
   - 检测 DNS 隧道通信
   - 使用 TF Session API
   - 模型: `/Agent/data/models/dnstun_model.pb`

3. **恶意 URL 检测** (`malice_url_filter.cpp`)
   - 检测恶意 URL
   - 使用 TF Session API
   - 模型: `/Agent/data/models/url_model.pb`

4. **挖矿检测** (`mining_filter.cpp`)
   - 检测加密货币挖矿活动

### 其他组件

- **threat_filter**: 威胁检测（不使用 TF API）
- **indexer**: 主索引引擎（重新编译以链接新 TF 库）

## 回滚方案

如果升级失败，可以回滚到 TF 2.0.4：

```bash
# 恢复旧库文件
cp /root/tf_backup/libtensorflow*.so* /usr/local/lib/
ldconfig

# 恢复旧头文件
rm -rf /usr/local/include/tf
mv /usr/local/include/tf_old_2.0.4 /usr/local/include/tf

# 恢复旧 indexer
cp /Agent/bin/indexer.backup /Agent/bin/indexer

# 重启服务
systemctl restart httpd
```

## 验证

升级完成后验证：

```bash
# 检查 TF 版本
ls -lh /usr/local/lib/libtensorflow_cc.so.2.12.0

# 检查 indexer 链接
ldd /Agent/bin/indexer | grep tensorflow

# 检查 AI 过滤器符号
nm /Agent/bin/indexer | grep -i "dga\|dnstun\|malice"

# 测试运行
/Agent/bin/indexer --help
```

## 时间估算

| 阶段 | 预计时间 |
|------|----------|
| 环境检查 | 1 分钟 |
| 安装依赖（Bazel） | 5-10 分钟 |
| 下载 TF 源码 | 10-30 分钟 |
| 编译 TF 2.12 | 4-8 小时 |
| 安装与重新编译 | 10-20 分钟 |
| **总计** | **约 5-9 小时** |

## 注意事项

1. **内存**: 编译 TF 需要大量内存，已添加 8GB swap
2. **磁盘**: 需要约 20GB 额外空间
3. **网络**: 需要下载约 1GB 文件
4. **中断**: 使用 `screen` 或 `nohup` 防止 SSH 断开导致编译中断
5. **模型文件**: 确保 `/Agent/data/models/` 下有对应的 `.pb` 模型文件

## 故障排除

### 编译失败：内存不足

```bash
# 增加 swap
dd if=/dev/zero of=/swapfile_extra bs=1G count=8
mkswap /swapfile_extra
swapon /swapfile_extra
```

### 编译失败：磁盘空间不足

```bash
# 清理 bazel 缓存
bazel clean --expunge
```

### 链接失败：找不到 TF 符号

```bash
# 检查库文件
ldconfig -p | grep tensorflow

# 手动刷新
ldconfig /usr/local/lib
```

## 联系与支持

如有问题，请检查：
1. 编译日志: `/tmp/tf_build.log`
2. 系统日志: `/var/log/messages`
3. indexer 日志: `/Agent/logs/indexer.log`
