"""定时调度服务 - 每天早上8:30自动触发工作流"""
import os
import time
import json
import logging
import requests
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/seat_push_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """工作流定时调度器"""
    
    def __init__(self, workflow_api_url: str = "http://localhost:5000/run"):
        """
        初始化调度器
        
        Args:
            workflow_api_url: 工作流API地址
        """
        self.workflow_api_url = workflow_api_url
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.execution_count = 0
        self.last_execution_time: Optional[str] = None
        
    def trigger_workflow(self):
        """
        触发工作流执行（同步方法）
        """
        try:
            logger.info(f"开始触发工作流，时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 调用工作流API
            response = requests.post(
                self.workflow_api_url,
                json={},
                timeout=300  # 5分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                self.execution_count += 1
                self.last_execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"✅ 工作流执行成功! 第{self.execution_count}次执行")
                logger.info(f"推送状态: {result.get('push_status', '未知')}")
                logger.info(f"分析结果数量: {len(result.get('analysis_result', {}).get('search_results', []))}")
            else:
                logger.error(f"❌ 工作流执行失败: HTTP {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                
        except requests.exceptions.Timeout:
            logger.error("❌ 工作流执行超时（超过5分钟）")
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 无法连接到工作流API: {self.workflow_api_url}")
            logger.error("请确保工作流服务已启动: python src/main.py -m http -p 5000")
        except Exception as e:
            logger.error(f"❌ 工作流执行异常: {str(e)}", exc_info=True)
    
    def setup_schedule(self, hour: int = 8, minute: int = 30):
        """
        设置定时任务
        
        Args:
            hour: 小时（24小时制）
            minute: 分钟
        """
        # 添加定时任务 - 每天指定时间执行
        self.scheduler.add_job(
            self.trigger_workflow,
            CronTrigger(hour=hour, minute=minute, timezone="Asia/Shanghai"),
            id='daily_push',
            name='每日汽车座椅产品规划推送',
            replace_existing=True
        )
        
        logger.info(f"✅ 定时任务已设置: 每天 {hour:02d}:{minute:02d} 执行")
        logger.info(f"📍 工作流API地址: {self.workflow_api_url}")
        logger.info(f"🕐 时区: Asia/Shanghai (北京时间)")
    
    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            logger.info("=" * 60)
            logger.info("🚀 定时调度服务已启动")
            logger.info("=" * 60)
            logger.info(f"📊 已执行次数: {self.execution_count}")
            if self.last_execution_time:
                logger.info(f"⏰ 上次执行: {self.last_execution_time}")
            logger.info("按 Ctrl+C 停止服务")
            logger.info("=" * 60)
            
            # 保持服务运行
            try:
                # 使用信号处理来保持进程运行
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
                
                # 主线程保持运行
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                self.stop()
                
        except Exception as e:
            logger.error(f"❌ 启动调度器失败: {str(e)}", exc_info=True)
            raise
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，准备停止服务...")
        self.stop()
        sys.exit(0)
    
    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            logger.info("正在停止调度服务...")
            self.scheduler.shutdown()
            logger.info("✅ 调度服务已停止")


def main():
    """主函数"""
    # 从环境变量获取配置，或使用默认值
    workflow_api_url = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:5000/run"
    )
    
    # 从环境变量获取执行时间，或使用默认值 8:30
    schedule_hour = int(os.getenv("SCHEDULE_HOUR", "8"))
    schedule_minute = int(os.getenv("SCHEDULE_MINUTE", "30"))
    
    # 创建调度器
    scheduler = WorkflowScheduler(workflow_api_url)
    
    # 设置定时任务
    scheduler.setup_schedule(hour=schedule_hour, minute=schedule_minute)
    
    # 启动服务
    scheduler.start()


if __name__ == "__main__":
    main()
