"""
量化交易系统主入口

运行方式：
    python quant/main.py

功能：
    - 加载所有量化策略任务
    - 启动任务调度器
    - 定时执行策略
"""

from quant.scheduler import TaskScheduler
from quant.tasks.high_open_2pct import HighOpen2PctTask
from quant.tasks.daily_data_download import DailyDataDownloadTask


def main():
    """
    主函数，初始化并启动量化任务调度器
    """
    # 创建调度器
    scheduler = TaskScheduler()
    
    # 添加策略任务
    tasks = [
        HighOpen2PctTask(),
        DailyDataDownloadTask(),
    ]
    
    scheduler.add_tasks(tasks)
    
    # 启动调度器
    scheduler.run()


if __name__ == '__main__':
    main()