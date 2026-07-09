from abc import ABC, abstractmethod
import time
from datetime import datetime


class BaseTask(ABC):
    """
    量化任务基类，所有任务都需要继承此类
    
    Attributes:
        schedule_time: 任务执行时间（格式: "HH:MM"）
        task_name: 任务名称
        enabled: 是否启用任务
    """
    
    def __init__(self, schedule_time: str, task_name: str):
        self.schedule_time = schedule_time
        self.task_name = task_name
        self.enabled = True
    
    @abstractmethod
    def run(self):
        """
        任务执行的核心逻辑，子类必须实现
        """
        pass
    
    def pre_run(self):
        """
        任务执行前的准备工作，可由子类重写
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行任务: {self.task_name}")
    
    def post_run(self):
        """
        任务执行后的清理工作，可由子类重写
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务执行完成: {self.task_name}")
    
    def execute(self):
        """
        执行任务的完整流程
        """
        if not self.enabled:
            return
        
        try:
            self.pre_run()
            self.run()
            self.post_run()
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务执行失败 {self.task_name}: {str(e)}")
    
    def get_schedule_time(self) -> str:
        """
        返回任务调度时间
        """
        return self.schedule_time
    
    def get_task_name(self) -> str:
        """
        返回任务名称
        """
        return self.task_name
    
    def set_enabled(self, enabled: bool):
        """
        设置任务是否启用
        """
        self.enabled = enabled
    
    def is_enabled(self) -> bool:
        """
        判断任务是否启用
        """
        return self.enabled