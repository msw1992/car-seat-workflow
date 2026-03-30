#!/bin/bash

# 查看定时调度服务状态

echo "========================================"
echo "📊 定时调度服务状态"
echo "========================================"

PID_FILE="/tmp/seat_push_scheduler.pid"
LOG_FILE="/tmp/seat_push_scheduler.log"

# 1. 检查进程状态
echo ""
echo "1️⃣ 进程状态："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$PID_FILE" ]; then
    SCHEDULER_PID=$(cat "$PID_FILE")
    
    if ps -p "$SCHEDULER_PID" > /dev/null 2>&1; then
        echo "   ✅ 服务正在运行"
        echo "   PID: $SCHEDULER_PID"
        echo ""
        
        # 显示进程详细信息
        echo "   进程详情："
        ps -p "$SCHEDULER_PID" -o pid,ppid,user,%cpu,%mem,etime,cmd | sed 's/^/   /'
    else
        echo "   ⚠️  服务已停止（PID文件存在但进程不存在）"
        echo "   建议执行: bash scripts/stop_scheduler.sh"
    fi
else
    echo "   ⚠️  服务未运行（无PID文件）"
fi

echo ""

# 2. 检查日志
echo "2️⃣ 日志文件："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    LOG_LINES=$(wc -l < "$LOG_FILE")
    
    echo "   📄 文件: $LOG_FILE"
    echo "   📊 大小: $LOG_SIZE"
    echo "   📝 行数: $LOG_LINES"
    echo ""
    
    # 显示最近的日志
    echo "   最近10条日志："
    echo "   ────────────────────────────────────"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
else
    echo "   ℹ️  日志文件不存在（服务可能未启动过）"
fi

echo ""

# 3. 检查执行时间配置
echo "3️⃣ 执行时间配置："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 从环境变量或默认值获取
SCHEDULE_HOUR=${SCHEDULE_HOUR:-8}
SCHEDULE_MINUTE=${SCHEDULE_MINUTE:-30}

echo "   ⏰ 每天执行: ${SCHEDULE_HOUR}:${SCHEDULE_MINUTE} (北京时间)"
echo "   🕐 时区: Asia/Shanghai"

echo ""

# 4. 下次执行时间
echo "4️⃣ 下次执行："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 计算下次执行时间
NOW=$(date +%s)
TODAY_SCHEDULE=$(date -d "${SCHEDULE_HOUR}:${SCHEDULE_MINUTE}" +%s 2>/dev/null || date -d "${SCHEDULE_HOUR}:${SCHEDULE_MINUTE} today" +%s)

if [ "$NOW" -lt "$TODAY_SCHEDULE" ]; then
    NEXT_RUN=$TODAY_SCHEDULE
    NEXT_RUN_TEXT="今天"
else
    # 明天
    NEXT_RUN=$(date -d "tomorrow ${SCHEDULE_HOUR}:${SCHEDULE_MINUTE}" +%s)
    NEXT_RUN_TEXT="明天"
fi

# 计算剩余秒数
REMAINING=$((NEXT_RUN - NOW))
HOURS=$((REMAINING / 3600))
MINUTES=$(((REMAINING % 3600) / 60))
SECONDS=$((REMAINING % 60))

echo "   📅 ${NEXT_RUN_TEXT}: $(date -d "@$NEXT_RUN" '+%Y-%m-%d %H:%M:%S')"
echo "   ⏳ 倒计时: ${HOURS}小时${MINUTES}分钟${SECONDS}秒"

echo ""

# 5. 管理命令提示
echo "5️⃣ 管理命令："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   启动服务: bash start_scheduler_daemon.sh"
echo "   停止服务: bash scripts/stop_scheduler.sh"
echo "   查看日志: tail -f $LOG_FILE"
echo "   查看配置: python scripts/check_schedule.py"
echo ""
echo "========================================"
