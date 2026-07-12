import time
import os
import json
import pickle
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from base_task import BaseTask
from util import get_stk_factor_pro, load_local_daily_data, save_local_daily_data


class DailyDataDownloadTask(BaseTask):
    """
    每日数据下载任务
    
    执行流程：
    1. 生成最近N天的日期列表
    2. 按日期遍历，调用stk_factor_pro获取当天所有股票数据
    3. 按ts_code分组整合数据
    4. 保留最近100天数据，原始数据保留3天份
    5. 使用pickle保存数据
    
    Attributes:
        data_path: 数据保存路径（pickle格式）
        download_days: 每次下载的天数
        keep_days: 保留的历史数据天数
    """
    
    def __init__(self):
        super().__init__(schedule_time="20:00", task_name="每日数据下载任务")
        
        self.download_days = 365
        self.keep_days = 3
        
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'quant', 'data'
        )
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.data_path = os.path.join(self.data_dir, 'daily_data.pkl')
        self.backup_path = os.path.join(self.data_dir, 'daily_data_backup.pkl')
    
    def _load_all_data(self) -> dict:
        """
        加载所有已保存的股票数据
        
        Returns:
            股票数据字典 {code: DataFrame}，如果文件不存在返回空字典
        """
        return load_local_daily_data(self.data_path)
    
    def _save_all_data(self, data: dict):
        """
        保存所有股票数据到pickle文件
        
        Args:
            data: 股票数据字典 {code: DataFrame}
        """
        save_local_daily_data(data, self.data_path)
    
    def _get_trade_dates(self, days: int) -> list:
        """
        生成最近N天的日期列表（格式：YYYYMMDD）
        
        Args:
            days: 天数
            
        Returns:
            日期字符串列表
        """
        dates = []
        today = datetime.now().date()
        
        for i in range(days):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%Y%m%d'))
        
        return dates
    
    def _download_date_data(self, trade_date: str) -> pd.DataFrame:
        """
        下载指定日期的所有股票数据
        
        Args:
            trade_date: 交易日期，格式如 '20260704'
            
        Returns:
            当天所有股票的数据DataFrame，如果获取失败返回空DataFrame
        """
        try:
            df = get_stk_factor_pro(trade_date=trade_date)
            
            if not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                
                columns_mapping = {
                    'open_qfq': 'open',
                    'close_qfq': 'close',
                    'high_qfq': 'high',
                    'low_qfq': 'low',
                    'vol': 'volume',
                    'pct_chg': 'pct_chg',
                    'turnover_rate_f': 'turnover_rate',
                    'volume_ratio': 'volume_ratio'
                }
                df = df.rename(columns={k: v for k, v in columns_mapping.items() if k in df.columns})
                
                keep_cols = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'pct_chg', 'turnover_rate', 'volume_ratio']
                df = df[keep_cols]
                
                return df
            
        except Exception as e:
            tqdm.write(f"获取日期 {trade_date} 数据失败: {str(e)}")
        
        return pd.DataFrame()
    
    def _backup_old_data(self):
        """
        备份旧数据（保留3天份）
        """
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'rb') as f:
                    old_data = pickle.load(f)
                
                with open(self.backup_path, 'wb') as f:
                    pickle.dump(old_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                print(f"已备份旧数据到: {self.backup_path}")
            except Exception as e:
                print(f"备份旧数据失败: {str(e)}")
    
    def run(self):
        """
        执行每日数据下载任务
        """
        
        print(f"\n{'='*60}")
        print("每日数据下载任务开始")
        print(f"日期: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"下载天数: {self.download_days}")
        print(f"{'='*60}")
        
        print("\n阶段1: 生成日期列表...")
        trade_dates = self._get_trade_dates(self.download_days)
        print(f"生成 {len(trade_dates)} 个日期，范围: {trade_dates[-1]} ~ {trade_dates[0]}")
        
        print("\n阶段2: 备份旧数据...")
        self._backup_old_data()
        
        print("\n阶段3: 按日期下载数据...")
        
        all_dfs = []
        success_dates = 0
        fail_dates = 0
        
        for trade_date in tqdm(trade_dates, desc="下载日期数据"):
            df = self._download_date_data(trade_date)
            
            if not df.empty:
                all_dfs.append(df)
                success_dates += 1
            else:
                fail_dates += 1
            
            time.sleep(0.1)
        
        if not all_dfs:
            print("\n警告：未获取到任何数据！")
            return
        
        print(f"\n阶段4: 整合数据...")
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        code2data = {}
        grouped = combined_df.groupby('ts_code')
        
        for ts_code, group in tqdm(grouped, desc="整合股票数据"):
            group = group.sort_values(by='trade_date', ascending=True)
            group = group.set_index('trade_date')
            group.index.name = ''
            group = group.drop(columns=['ts_code'])
            
            code2data[ts_code] = group
        
        print(f"\n阶段5: 保存数据...")
        self._save_all_data(code2data)
        print(f"数据已保存到: {self.data_path}")
        
        print(f"\n{'='*60}")
        print("下载完成")
        print(f"成功日期: {success_dates} 天")
        print(f"失败日期: {fail_dates} 天")
        print(f"总股票数: {len(code2data)} 只")
        print(f"总记录数: {len(combined_df)} 条")
        print(f"{'='*60}")
        
        self._save_log(success_dates, fail_dates, len(code2data), len(combined_df))
    
    def _save_log(self, success_dates: int, fail_dates: int, total_stocks: int, total_records: int):
        """
        保存任务执行日志
        
        Args:
            success_dates: 成功下载日期数
            fail_dates: 失败日期数
            total_stocks: 总股票数
            total_records: 总记录数
        """
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'quant', 'logs'
        )
        os.makedirs(log_dir, exist_ok=True)
        
        log_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'task_name': self.task_name,
            'download_days': self.download_days,
            'keep_days': self.keep_days,
            'success_dates': success_dates,
            'fail_dates': fail_dates,
            'total_stocks': total_stocks,
            'total_records': total_records,
            'data_path': self.data_path,
            'backup_path': self.backup_path
        }
        
        filename = f"daily_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='每日数据下载任务')
    parser.add_argument('--days', type=int, default=100, help='下载天数')
    args = parser.parse_args()
    
    task = DailyDataDownloadTask()
    if args.days > 0:
        task.download_days = args.days
    task.execute()