"""
检查定时服务配置状态
"""
import os
import sys
from datetime import datetime

def check_schedule():
    """检查定时任务配置"""
    
    print("=" * 60)
    print("📋 定时任务配置检查")
    print("=" * 60)
    print()
    
    # 1. 检查环境变量
    print("1️⃣ 环境变量配置：")
    schedule_hour = os.getenv("SCHEDULE_HOUR", "未设置（使用默认值）")
    schedule_minute = os.getenv("SCHEDULE_MINUTE", "未设置（使用默认值）")
    
    print(f"   SCHEDULE_HOUR: {schedule_hour}")
    print(f"   SCHEDULE_MINUTE: {schedule_minute}")
    print()
    
    # 2. 显示实际执行时间
    print("2️⃣ 实际执行时间：")
    
    # 获取最终生效的时间
    hour = int(os.getenv("SCHEDULE_HOUR", "8"))
    minute = int(os.getenv("SCHEDULE_MINUTE", "30"))
    
    print(f"   ⏰ 每天执行时间: {hour:02d}:{minute:02d} (北京时间)")
    print(f"   🕐 时区: Asia/Shanghai")
    print()
    
    # 3. 计算下次执行时间
    print("3️⃣ 下次执行时间：")
    now = datetime.now()
    
    # 构建今天的执行时间
    today_execute = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if now < today_execute:
        # 今天还没到执行时间
        next_run = today_execute
        print(f"   📅 今天: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # 今天已过执行时间，下次是明天
        next_run = today_execute.replace(day=now.day + 1)
        print(f"   📅 明天: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 计算剩余时间
    time_diff = next_run - now
    hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"   ⏳ 距离下次执行: {hours}小时{minutes}分钟{seconds}秒")
    print()
    
    # 4. 检查服务状态
    print("4️⃣ 服务状态检查：")
    
    # 检查日志文件
    log_file = "/tmp/seat_push_scheduler.log"
    if os.path.exists(log_file):
        print(f"   ✅ 日志文件存在: {log_file}")
        
        # 读取最后几行日志
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) > 5 else lines
                
                print(f"   📝 最近日志记录：")
                for line in last_lines:
                    print(f"      {line.strip()}")
        except Exception as e:
            print(f"   ⚠️  读取日志失败: {str(e)}")
    else:
        print(f"   ℹ️  日志文件不存在（服务可能未启动过）")
    
    print()
    
    # 5. 配置建议
    print("5️⃣ 配置建议：")
    print()
    print("   如需修改执行时间，可通过以下方式：")
    print()
    print("   方式1：修改环境变量（临时）")
    print(f'   export SCHEDULE_HOUR="9"')
    print(f'   export SCHEDULE_MINUTE="00"')
    print()
    print("   方式2：修改启动脚本（永久）")
    print("   编辑 start_scheduler.sh，取消注释并修改：")
    print(f'   export SCHEDULE_HOUR="9"')
    print(f'   export SCHEDULE_MINUTE="00"')
    print()
    
    print("=" * 60)
    print("✅ 检查完成")
    print("=" * 60)


if __name__ == "__main__":
    check_schedule()
