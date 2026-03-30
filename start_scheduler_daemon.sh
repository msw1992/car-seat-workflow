#!/bin/bash

# 汽车座椅产品规划定时推送服务 - 后台运行版本
# 功能：每天早上8:30自动执行工作流，即使关闭网页也继续运行

echo "========================================"
echo "🚀 汽车座椅产品规划定时推送服务（后台模式）"
echo "========================================"

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi

# 检查依赖是否已安装
echo "🔍 检查依赖..."
pip install -q apscheduler requests

# 日志文件路径
LOG_FILE="/tmp/seat_push_scheduler.log"
PID_FILE="/tmp/seat_push_scheduler.pid"

# 检查是否已有进程在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  定时服务已在运行中 (PID: $OLD_PID)"
        echo ""
        echo "如需重启，请先执行："
        echo "  bash scripts/stop_scheduler.sh"
        echo ""
        echo "查看运行状态："
        echo "  tail -f $LOG_FILE"
        exit 1
    else
        echo "🧹 清理旧的PID文件..."
        rm -f "$PID_FILE"
    fi
fi

# 设置环境变量（可选）
# export WORKFLOW_API_URL="http://localhost:5000/run"
# export SCHEDULE_HOUR="8"
# export SCHEDULE_MINUTE="30"

# 启动定时服务（后台运行）
echo "🚀 启动定时调度服务（后台模式）..."
nohup python src/scheduler/scheduler_service.py >> "$LOG_FILE" 2>&1 &

# 获取进程PID
SCHEDULER_PID=$!
echo "$SCHEDULER_PID" > "$PID_FILE"

echo ""
echo "✅ 定时服务已启动"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 服务信息："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   进程ID (PID): $SCHEDULER_PID"
echo "   日志文件: $LOG_FILE"
echo "   PID文件: $PID_FILE"
echo "   执行时间: 每天 08:30 (北京时间)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 管理命令："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  查看实时日志："
echo "    tail -f $LOG_FILE"
echo ""
echo "  查看进程状态："
echo "    ps -p $SCHEDULER_PID"
echo ""
echo "  停止服务："
echo "    bash scripts/stop_scheduler.sh"
echo ""
echo "  检查配置："
echo "    python scripts/check_schedule.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 提示：关闭此终端后服务将继续运行"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
