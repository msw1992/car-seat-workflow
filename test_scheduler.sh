#!/bin/bash

# 测试定时调度服务

echo "========================================"
echo "测试定时调度服务"
echo "========================================"

# 启动工作流服务（如果未运行）
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "⚠️  工作流服务未启动，正在启动..."
    python src/main.py -m http -p 5000 &
    WORKFLOW_PID=$!
    sleep 5
    echo "✅ 工作流服务已启动 (PID: $WORKFLOW_PID)"
else
    echo "✅ 工作流服务已运行"
fi

echo ""
echo "========================================"
echo "启动定时调度服务（测试模式）"
echo "========================================"
echo "服务将在5秒后自动停止..."
echo ""

# 启动定时服务并在5秒后停止
timeout 5 python src/scheduler/scheduler_service.py || true

echo ""
echo "========================================"
echo "✅ 测试完成"
echo "========================================"
echo ""
echo "生产环境启动方式："
echo "  bash start_scheduler.sh"
echo ""
