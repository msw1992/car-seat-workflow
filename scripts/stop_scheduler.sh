#!/bin/bash

# 停止定时调度服务

echo "========================================"
echo "🛑 停止定时调度服务"
echo "========================================"

PID_FILE="/tmp/seat_push_scheduler.pid"

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  未找到PID文件，服务可能未运行"
    echo ""
    echo "尝试查找并终止所有相关进程..."
    pkill -f "scheduler_service.py"
    echo "✅ 已尝试终止所有相关进程"
    exit 0
fi

# 读取PID
SCHEDULER_PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p "$SCHEDULER_PID" > /dev/null 2>&1; then
    echo "⚠️  进程 $SCHEDULER_PID 不存在，清理PID文件..."
    rm -f "$PID_FILE"
    exit 0
fi

# 终止进程
echo "正在停止进程 $SCHEDULER_PID ..."
kill "$SCHEDULER_PID"

# 等待进程结束
sleep 2

# 检查是否成功停止
if ps -p "$SCHEDULER_PID" > /dev/null 2>&1; then
    echo "⚠️  进程未响应，强制终止..."
    kill -9 "$SCHEDULER_PID"
    sleep 1
fi

# 清理PID文件
rm -f "$PID_FILE"

echo ""
echo "✅ 定时调度服务已停止"
echo ""
