#!/bin/bash

# 重新配置定时服务为 16:15 执行（用于测试）

echo "========================================"
echo "🔧 重新配置定时服务"
echo "========================================"
echo ""

# 1. 停止当前服务
echo "1️⃣ 停止当前服务..."
bash scripts/stop_scheduler.sh
sleep 2

# 2. 设置环境变量
echo ""
echo "2️⃣ 设置执行时间为 16:15..."
export SCHEDULE_HOUR="16"
export SCHEDULE_MINUTE="15"

# 3. 重新启动
echo ""
echo "3️⃣ 重新启动服务..."
bash start_scheduler_daemon.sh

echo ""
echo "========================================"
echo "✅ 配置完成"
echo "========================================"
echo ""
echo "执行时间已修改为: 每天 16:15"
echo ""
echo "验证配置: bash scripts/scheduler_status.sh"
echo "查看日志: tail -f /tmp/seat_push_scheduler.log"
