# 定时服务后台运行配置指南

## 问题说明

**问题**：执行 `bash start_scheduler.sh` 后，关闭网页/终端，定时任务是否会继续执行？

**答案**：
- ❌ 使用 `start_scheduler.sh`：关闭网页后会停止
- ✅ 使用 `start_scheduler_daemon.sh`：关闭网页后继续运行

## 原因分析

### 前台进程 vs 后台进程

| 启动方式 | 进程类型 | 关闭终端后 | 适用场景 |
|---------|---------|-----------|---------|
| `python script.py` | 前台进程 | 进程终止 | 临时测试、调试 |
| `nohup python script.py &` | 后台进程 | 继续运行 | 生产环境、长期运行 |

### 进程关系

```
终端/SSH会话
  └─ bash start_scheduler.sh
      └─ python scheduler_service.py  (前台进程)
          ↑
          关闭终端时，会话结束，进程被终止
```

```
终端/SSH会话
  └─ bash start_scheduler_daemon.sh
      └─ nohup python scheduler_service.py &  (后台进程)
          ↑
          nohup 使进程忽略 SIGHUP 信号
          关闭终端时，进程继续运行
```

## 解决方案

### 方案1：使用后台运行脚本（推荐）

**启动服务：**
```bash
# 1. 先启动工作流HTTP服务
python src/main.py -m http -p 5000 &

# 2. 启动定时调度服务（后台运行）
bash start_scheduler_daemon.sh
```

**特点：**
- ✅ 使用 `nohup` 实现后台运行
- ✅ 自动记录 PID，方便管理
- ✅ 日志输出到文件
- ✅ 关闭网页/终端后继续运行

### 方案2：使用 screen 或 tmux（可选）

**使用 screen：**
```bash
# 安装 screen
apt-get install screen  # Ubuntu/Debian
yum install screen      # CentOS/RHEL

# 创建新会话
screen -S scheduler

# 启动服务
bash start_scheduler.sh

# 按 Ctrl+A 然后按 D 分离会话
# 关闭终端后进程继续运行

# 重新连接会话
screen -r scheduler
```

**使用 tmux：**
```bash
# 安装 tmux
apt-get install tmux  # Ubuntu/Debian
yum install tmux      # CentOS/RHEL

# 创建新会话
tmux new -s scheduler

# 启动服务
bash start_scheduler.sh

# 按 Ctrl+B 然后按 D 分离会话
# 关闭终端后进程继续运行

# 重新连接会话
tmux attach -t scheduler
```

### 方案3：使用 systemd 服务（生产环境推荐）

**创建服务文件：**
```bash
sudo tee /etc/systemd/system/seat-push-scheduler.service > /dev/null <<EOF
[Unit]
Description=Car Seat Product Planning Daily Push Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 src/scheduler/scheduler_service.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/tmp/seat_push_scheduler.log
StandardError=append:/tmp/seat_push_scheduler.log

[Install]
WantedBy=multi-user.target
EOF
```

**启动服务：**
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start seat-push-scheduler

# 开机自启动
sudo systemctl enable seat-push-scheduler

# 查看状态
sudo systemctl status seat-push-scheduler

# 查看日志
sudo journalctl -u seat-push-scheduler -f
```

## 管理命令

### 查看服务状态
```bash
bash scripts/scheduler_status.sh
```

### 查看实时日志
```bash
tail -f /tmp/seat_push_scheduler.log
```

### 停止服务
```bash
bash scripts/stop_scheduler.sh
```

### 重启服务
```bash
# 停止
bash scripts/stop_scheduler.sh

# 启动
bash start_scheduler_daemon.sh
```

### 检查配置
```bash
python scripts/check_schedule.py
```

## 文件说明

| 文件 | 说明 |
|-----|------|
| `start_scheduler_daemon.sh` | 后台启动脚本（推荐） |
| `scripts/stop_scheduler.sh` | 停止服务脚本 |
| `scripts/scheduler_status.sh` | 查看状态脚本 |
| `scripts/check_schedule.py` | 配置检查工具 |
| `/tmp/seat_push_scheduler.pid` | PID文件 |
| `/tmp/seat_push_scheduler.log` | 日志文件 |

## 常见问题

### Q1: 如何确认服务是否在后台运行？

```bash
# 方式1：查看PID文件
cat /tmp/seat_push_scheduler.pid

# 方式2：查看进程
ps aux | grep scheduler_service.py

# 方式3：使用状态脚本
bash scripts/scheduler_status.sh
```

### Q2: 服务启动失败怎么办？

```bash
# 1. 查看日志
tail -20 /tmp/seat_push_scheduler.log

# 2. 检查工作流服务是否启动
curl http://localhost:5000/run

# 3. 检查Python依赖
pip list | grep apscheduler
pip list | grep requests

# 4. 手动测试
python src/scheduler/scheduler_service.py
```

### Q3: 如何修改执行时间？

```bash
# 方式1：环境变量（临时）
export SCHEDULE_HOUR="9"
export SCHEDULE_MINUTE="00"
bash start_scheduler_daemon.sh

# 方式2：修改脚本（永久）
vim start_scheduler_daemon.sh
# 取消注释并修改环境变量
```

### Q4: 如何确保服务开机自启动？

**推荐使用 systemd 服务**（见方案3），可以：
- ✅ 开机自动启动
- ✅ 服务崩溃自动重启
- ✅ 统一的日志管理
- ✅ 方便的启停控制

## 最佳实践

### 生产环境部署建议

1. **使用 systemd 服务**
   - 可靠性高，开机自启
   - 自动重启机制
   - 集中式日志管理

2. **监控服务状态**
   - 定期检查日志
   - 设置告警通知
   - 监控进程状态

3. **日志轮转**
   - 定期清理日志文件
   - 设置日志大小限制
   - 使用 logrotate 管理

4. **备份与恢复**
   - 定期备份配置文件
   - 记录部署信息
   - 准备回滚方案

## 总结

| 场景 | 推荐方案 | 启动命令 |
|-----|---------|---------|
| 开发测试 | 前台运行 | `bash start_scheduler.sh` |
| 生产环境 | 后台运行 | `bash start_scheduler_daemon.sh` |
| 企业部署 | systemd服务 | `systemctl start seat-push-scheduler` |

**推荐：** 日常使用 `bash start_scheduler_daemon.sh` 启动，关闭网页后服务继续运行。
