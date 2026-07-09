import schedule
import time
import threading
from datetime import datetime
from typing import List, Optional
from base_task import BaseTask


class TaskScheduler:
    """
    任务调度器，管理所有量化任务的定时执行
    
    Attributes:
        tasks: 任务列表
        running: 是否正在运行
        thread_pool: 线程池（用于运行任务）
    """
    
    def __init__(self):
        self.tasks: List[BaseTask] = []
        self.running = False
    
    def add_task(self, task: BaseTask):
        """
        添加任务到调度器
        
        Args:
            task: BaseTask子类实例
        """
        self.tasks.append(task)
        print(f"已添加任务: {task.get_task_name()}，调度时间: {task.get_schedule_time()}")
    
    def add_tasks(self, tasks: List[BaseTask]):
        """
        批量添加任务
        
        Args:
            tasks: BaseTask实例列表
        """
        for task in tasks:
            self.add_task(task)
    
    def schedule_all(self):
        """
        调度所有任务
        """
        for task in self.tasks:
            if task.is_enabled():
                schedule_time = task.get_schedule_time()
                schedule.every().day.at(schedule_time).do(
                    self._execute_task_async, task
                )
                print(f"任务 {task.get_task_name()} 已调度到每天 {schedule_time}")
    
    def _execute_task_async(self, task: BaseTask):
        """
        在后台线程中执行任务（内部方法）
        
        Args:
            task: BaseTask实例
        """
        thread = threading.Thread(target=self._execute_task, args=(task,))
        thread.daemon = True
        thread.start()
    
    def _execute_task(self, task: BaseTask):
        """
        执行单个任务（内部方法）
        
        Args:
            task: BaseTask实例
        """
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务线程启动: {task.get_task_name()}")
        print(f"线程ID: {threading.current_thread().ident}")
        print(f"{'='*60}")
        
        try:
            task.execute()
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务执行异常 {task.get_task_name()}: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务线程结束: {task.get_task_name()}")
        print(f"{'='*60}\n")
    
    def run(self):
        """
        启动调度器，开始循环执行任务
        """
        if not self.tasks:
            print("警告：没有任务需要调度")
            return
        
        self.schedule_all()
        self.running = True
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务调度器已启动")
        print(f"共调度 {len(self.tasks)} 个任务")
        print("按 Ctrl+C 停止调度器\n")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """
        停止调度器
        """
        self.running = False
        schedule.clear()
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任务调度器已停止")
    
    def get_tasks(self) -> List[BaseTask]:
        """
        返回所有任务列表
        
        Returns:
            任务列表
        """
        return self.tasks
    
    def get_task_by_name(self, task_name: str) -> Optional[BaseTask]:
        """
        根据任务名称获取任务
        
        Args:
            task_name: 任务名称
        
        Returns:
            BaseTask实例或None
        """
        for task in self.tasks:
            if task.get_task_name() == task_name:
                return task
        return None