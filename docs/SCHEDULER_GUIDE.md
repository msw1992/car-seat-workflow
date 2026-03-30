# 汽车座椅产品规划定时推送服务 - 使用指南

## 🎯 功能说明

**完全自动化的定时推送方案**，无需任何人工干预：

```
⏰ 每天早上 8:30
    ↓
🔄 自动触发工作流
    ↓
🔍 搜索最新汽车座椅资讯
    ↓
🤖 AI分析生成产品规划建议
    ↓
📱 自动推送到飞书群
    ↓
✅ 完成
```

---

## 🚀 快速启动（3步）

### 步骤1：启动工作流HTTP服务

```bash
# 方式一：后台启动
python src/main.py -m http -p 5000 &

# 方式二：前台启动（可看到实时日志）
python src/main.py -m http -p 5000
```

### 步骤2：启动定时调度服务

```bash
# 方式一：使用启动脚本
bash start_scheduler.sh

# 方式二：直接运行
python src/scheduler/scheduler_service.py
```

### 步骤3：验证服务状态

看到以下输出表示启动成功：

```
============================================================
🚀 定时调度服务已启动
============================================================
✅ 定时任务已设置: 每天 08:30 执行
📍 工作流API地址: http://localhost:5000/run
🕐 时区: Asia/Shanghai (北京时间)
📊 已执行次数: 0
按 Ctrl+C 停止服务
============================================================
```

---

## ⚙️ 配置说明

### 自定义执行时间

通过环境变量配置：

```bash
# 设置执行时间为每天早上9点
export SCHEDULE_HOUR=9
export SCHEDULE_MINUTE=0

# 启动服务
python src/scheduler/scheduler_service.py
```

### 自定义工作流API地址

```bash
# 如果工作流部署在服务器上
export WORKFLOW_API_URL="http://your-server-ip:5000/run"

# 启动服务
python src/scheduler/scheduler_service.py
```

---

## 📊 监控与日志

### 查看日志

```bash
# 实时查看日志
tail -f /tmp/seat_push_scheduler.log

# 查看最近20行日志
tail -n 20 /tmp/seat_push_scheduler.log
```

### 日志示例

```
2024-03-30 08:30:00 - __main__ - INFO - 开始触发工作流，时间: 2024-03-30 08:30:00
2024-03-30 08:30:45 - __main__ - INFO - ✅ 工作流执行成功! 第1次执行
2024-03-30 08:30:45 - __main__ - INFO - 推送状态: 推送成功
2024-03-30 08:30:45 - __main__ - INFO - 分析结果数量: 15
```

---

## 🛠️ 生产环境部署

### 方案一：Systemd服务（推荐）

**1. 创建服务文件**

```bash
sudo nano /etc/systemd/system/seat-push-workflow.service
```

内容：
```ini
[Unit]
Description=Seat Push Workflow HTTP Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/projects
ExecStart=/usr/bin/python3 /workspace/projects/src/main.py -m http -p 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. 创建定时服务文件**

```bash
sudo nano /etc/systemd/system/seat-push-scheduler.service
```

内容：
```ini
[Unit]
Description=Seat Push Scheduler Service
After=network.target seat-push-workflow.service
Requires=seat-push-workflow.service

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/projects
Environment="WORKFLOW_API_URL=http://localhost:5000/run"
Environment="SCHEDULE_HOUR=8"
Environment="SCHEDULE_MINUTE=30"
ExecStart=/usr/bin/python3 /workspace/projects/src/scheduler/scheduler_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. 启动服务**

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable seat-push-workflow
sudo systemctl enable seat-push-scheduler

# 启动服务
sudo systemctl start seat-push-workflow
sudo systemctl start seat-push-scheduler

# 查看状态
sudo systemctl status seat-push-scheduler
```

**4. 管理服务**

```bash
# 停止服务
sudo systemctl stop seat-push-scheduler

# 重启服务
sudo systemctl restart seat-push-scheduler

# 查看日志
sudo journalctl -u seat-push-scheduler -f
```

---

### 方案二：Docker Compose

**创建 `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # 工作流HTTP服务
  workflow:
    build: .
    ports:
      - "5000:5000"
    command: python src/main.py -m http -p 5000
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 定时调度服务
  scheduler:
    build: .
    depends_on:
      - workflow
    environment:
      - WORKFLOW_API_URL=http://workflow:5000/run
      - SCHEDULE_HOUR=8
      - SCHEDULE_MINUTE=30
    command: python src/scheduler/scheduler_service.py
    restart: always
    volumes:
      - ./logs:/tmp
```

**启动：**

```bash
docker-compose up -d
```

---

## 🔍 故障排查

### 问题1：服务启动失败

**症状：** `❌ 无法连接到工作流API`

**解决方案：**
```bash
# 检查工作流服务是否启动
curl http://localhost:5000/health

# 如果未启动，先启动工作流服务
python src/main.py -m http -p 5000
```

### 问题2：定时任务未执行

**检查步骤：**
```bash
# 1. 检查服务状态
sudo systemctl status seat-push-scheduler

# 2. 检查日志
tail -f /tmp/seat_push_scheduler.log

# 3. 检查时区设置
timedatectl
```

### 问题3：执行失败

**查看详细错误：**
```bash
# 查看工作流日志
tail -f /app/work/logs/bypass/app.log

# 查看调度器日志
tail -f /tmp/seat_push_scheduler.log
```

---

## 📈 性能优化

### 并发控制
- 工作流服务支持并发请求
- 调度器自动重试失败的请求

### 资源监控
```bash
# 查看进程资源占用
ps aux | grep scheduler

# 查看内存使用
free -h
```

---

## ✅ 最佳实践

1. **生产环境推荐使用 Systemd 服务**
   - 开机自启
   - 自动重启
   - 日志管理

2. **定期检查日志**
   - 设置日志轮转
   - 监控异常情况

3. **备份配置**
   - 保存环境变量配置
   - 备份服务文件

4. **测试验证**
   - 首次部署后手动触发测试
   - 观察日志确认执行正常

---

## 🎁 额外功能

### 手动触发执行

如果需要立即执行一次（不等待定时）：

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 修改执行时间

无需重启服务，修改环境变量后重启即可：

```bash
# 修改为每天早上9点
export SCHEDULE_HOUR=9
export SCHEDULE_MINUTE=0

# 重启服务
sudo systemctl restart seat-push-scheduler
```

---

## 📞 技术支持

如遇问题，请检查：
1. 工作流服务是否正常运行
2. 调度服务日志是否有错误
3. 网络连接是否正常
4. 时区设置是否正确

更多信息请查看 `AGENTS.md` 文件。
