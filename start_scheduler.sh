#!/bin/bash

# 汽车座椅产品规划定时推送服务启动脚本
# 功能：每天早上8:30自动执行工作流

echo "========================================"
echo "🚀 汽车座椅产品规划定时推送服务"
echo "========================================"

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi

# 检查依赖是否已安装
echo "🔍 检查依赖..."
pip install -q apscheduler requests

# 设置环境变量（可选）
# export WORKFLOW_API_URL="http://localhost:5000/run"
# export SCHEDULE_HOUR="8"
# export SCHEDULE_MINUTE="30"

# 启动定时服务
echo "🚀 启动定时调度服务..."
python src/scheduler/scheduler_service.py
