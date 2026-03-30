# 定时推送服务 - 快速启动指南

## ✅ 问题已解决

修复了 `RuntimeError: no running event loop` 错误，现在服务可以正常启动！

---

## 🚀 快速启动（2步）

### 第1步：启动工作流服务

```bash
# 后台启动
python src/main.py -m http -p 5000 &

# 或者前台启动（可看到实时日志）
python src/main.py -m http -p 5000
```

### 第2步：启动定时服务

```bash
bash start_scheduler.sh
```

---

## ✅ 成功标志

看到以下输出表示启动成功：

```
✅ 定时任务已设置: 每天 08:30 执行
📍 工作流API地址: http://localhost:5000/run
🕐 时区: Asia/Shanghai (北京时间)
============================================================
🚀 定时调度服务已启动
============================================================
📊 已执行次数: 0
按 Ctrl+C 停止服务
============================================================
```

---

## 📅 工作原理

```
⏰ 每天早上 8:30
    ↓
🔄 自动触发工作流
    ↓
🔍 搜索最近一周汽车座椅资讯（20条）
    ↓
📚 从知识库 Car_Seat 检索相关知识（10条）
    ↓
🤖 AI分析生成产品规划建议
    ↓
📱 自动推送到飞书群（含当日日期）
    ↓
✅ 完成
```

---

## ⚙️ 自定义配置

### 修改执行时间

```bash
# 设置执行时间为每天早上9点
export SCHEDULE_HOUR=9
export SCHEDULE_MINUTE=0

# 启动服务
bash start_scheduler.sh
```

### 修改工作流API地址

```bash
# 如果工作流部署在服务器上
export WORKFLOW_API_URL="http://your-server:5000/run"

# 启动服务
bash start_scheduler.sh
```

---

## 📊 监控与日志

### 查看日志

```bash
# 实时查看日志
tail -f /tmp/seat_push_scheduler.log

# 查看最近50行日志
tail -n 50 /tmp/seat_push_scheduler.log
```

### 停止服务

按 `Ctrl+C` 即可优雅停止服务。

---

## 🧪 测试验证

运行测试脚本：

```bash
bash test_scheduler.sh
```

---

## 🏭 生产环境部署

### 使用 Systemd 服务（推荐）

```bash
# 1. 复制服务文件
sudo cp scripts/deploy_scheduler.sh /etc/systemd/system/seat-push.service

# 2. 启用并启动
sudo systemctl enable seat-push
sudo systemctl start seat-push

# 3. 查看状态
sudo systemctl status seat-push
```

---

## 🎁 额外功能

### 手动触发执行

```bash
curl -X POST http://localhost:5000/run
```

### 检查服务健康

```bash
curl http://localhost:5000/health
```

---

## ❓ 常见问题

### Q: 如何确认服务正在运行？

```bash
# 查看进程
ps aux | grep scheduler_service

# 查看日志
tail -f /tmp/seat_push_scheduler.log
```

### Q: 如何修改推送时间？

编辑环境变量后重启服务即可：

```bash
export SCHEDULE_HOUR=9
export SCHEDULE_MINUTE=0
bash start_scheduler.sh
```

### Q: 服务会自动重启吗？

- 使用 `bash start_scheduler.sh` 启动时，不会自动重启
- 使用 Systemd 服务部署时，会自动重启

---

## 📖 详细文档

查看完整文档：`docs/SCHEDULER_GUIDE.md`

---

## ✅ 状态

- [x] 服务启动正常
- [x] 定时任务配置正确
- [x] 时区设置正确（Asia/Shanghai）
- [x] 日志记录完整
- [x] 支持优雅停止

**现在你可以启动服务，之后每天早上8:30会自动推送消息到飞书！** 🎉
