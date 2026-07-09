import time
import json
import os
import pickle
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from base_task import BaseTask
from util import get_stock_codes, get_price_pro, add_exchange_suffix, add_exchange_prefix, load_local_daily_data


try:
    from Ashare import get_price
    ASHARE_AVAILABLE = True
except ImportError as e:
    ASHARE_AVAILABLE = False
    print("警告：无法导入Ashare库", e)  


class HighOpen2PctTask(BaseTask):
    """
    连续2日涨停 + 当日高开2个点策略
    
    执行流程：
    1. 9:20 预计算阶段：获取所有股票近13日数据，筛选连续2日涨停股票
    2. 9:26 竞价结束后：获取连板股票当日开盘价，筛选高开2个点以上的股票
    
    Attributes:
        limit_up_codes: 连续涨停股票代码列表（阶段1结果）
        code2price: 股票代码到价格数据的映射
        LIMIT_UP_THRESH: 涨停阈值（默认10%容错）
        OPEN_UP_THRESH: 高开阈值（2个点）
        MAX_RETRY: 获取开盘价时的最大重试次数
        RETRY_INTERVAL: 重试间隔（秒）
        dry_run: 是否为模拟运行模式
        results_dir: 结果保存目录
    """
    
    def __init__(self, dry_run=False):
        super().__init__(schedule_time="09:20", task_name="连续涨停高开2点策略")
        
        self.limit_up_codes = []
        self.code2price = {}
        self.dry_run = dry_run
        
        # 阈值设置
        self.LIMIT_UP_THRESH = 1.098  # 10%涨停容错阈值
        self.OPEN_UP_THRESH = 1.02    # 高开2个点阈值
        
        # 重试设置
        self.MAX_RETRY = 30
        self.RETRY_INTERVAL = 2
        
        # 结果保存目录
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'quant', 'results'
        )
        os.makedirs(self.results_dir, exist_ok=True)
    
    
    def _fetch_daily_data(self, total_codes: list) -> dict:
        """
        获取所有股票的近30日日线数据
        
        优先使用本地数据，本地数据不足时使用API补充
        
        Args:
            total_codes: 股票代码列表（不带前缀/后缀）
        
        Returns:
            股票代码到DataFrame的映射（key为不带前缀的原始代码）
        """
        code2price = {}
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始获取 {len(total_codes)} 只股票的日线数据...")
        
        local_data = load_local_daily_data()
        
        if local_data:
            print(f"发现本地数据，包含 {len(local_data)} 只股票")
            
            for stock in total_codes:
                ts_code = add_exchange_suffix(stock)
                if ts_code in local_data and not local_data[ts_code].empty:
                    df = local_data[ts_code].sort_index(ascending=True)
                    code2price[stock] = df.iloc[-13:]
            
            print(f"从本地数据加载了 {len(code2price)} 只股票")
        
        missing_codes = [code for code in total_codes if code not in code2price]
        
        if missing_codes:
            print(f"本地数据缺少 {len(missing_codes)} 只股票，使用API补充...")
            
            for stock in tqdm(missing_codes, desc="API补充数据"):
                try:
                    stock_code = add_exchange_prefix(stock, sep='')
                    price = get_price(stock_code, frequency='1d', count=13)
                    
                    if not price.empty:
                        code2price[stock] = price
                    
                    time.sleep(0.05)
                    
                except Exception as e:
                    tqdm.write(f"获取 {stock} 数据失败: {str(e)}")
                    continue
        
        print(f"成功获取 {len(code2price)} 只股票的日线数据")
        return code2price
    
    # def _filter_limit_up_codes(self, code2price: dict) -> list:
    #     """
    #     筛选连续两日涨停的股票
        
    #     Args:
    #         code2price: 股票代码到价格数据的映射
        
    #     Returns:
    #         连续涨停股票代码列表
    #     """
    #     limit_up_codes = []
        
    #     print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始筛选连续涨停股票...")
        
    #     for stock, df in tqdm(code2price.items(), desc="筛选连板股票"):
    #         if df.empty or len(df) < 2:
    #             continue
            
    #         df = df.sort_index(ascending=True)
            
    #         df['pct'] = df['close'] / df['close'].shift(1)
    #         df['limit_up'] = df['pct'] >= self.LIMIT_UP_THRESH
            
    #         df['two_consec'] = df['limit_up'] & df['limit_up'].shift(1)
            
    #         if df['two_consec'].any():
    #             limit_up_codes.append(stock)
        
    #     print(f"连续两天涨停个股数量: {len(limit_up_codes)}")
    #     return limit_up_codes

    def _filter_limit_up_codes(self, code2price: dict) -> list:
        """
        筛选连续两日涨停的股票
        
        Args:
            code2price: 股票代码到价格数据的映射
        
        Returns:
            连续涨停股票代码列表
        """
        limit_up_codes = []
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始筛选连续涨停股票...")
        
        for stock, df in tqdm(code2price.items(), desc="筛选连板股票"):
            if df.empty or len(df) < 2:
                continue
            
            df = df.sort_index(ascending=True)
            
            # df['pct'] = df['close'] / df['close'].shift(1)
            df['limit_up'] = df['pct_chg'] >= self.LIMIT_UP_THRESH
            
            df['two_consec'] = df['limit_up'] & df['limit_up'].shift(1)
            
            if df['two_consec'].any():
                limit_up_codes.append(stock)
        
        print(f"连续两天涨停个股数量: {len(limit_up_codes)}")
        return limit_up_codes
    
    def _get_opening_price(self, stock_code: str) -> float:
        """
        获取股票当日开盘价（09:30:00第一根分钟线）
        
        Args:
            stock_code: 股票代码
        
        Returns:
            当日开盘价，如果获取失败返回None
        """
        for attempt in range(self.MAX_RETRY):
            try:
                current_price = get_price(stock_code, frequency='1m', count=100)
                
                if current_price.empty:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                
                # 筛选今日数据
                today = datetime.now().date()
                current_price = current_price[current_price.index.date == today]
                
                if current_price.empty:
                    time.sleep(self.RETRY_INTERVAL)
                    continue
                
                # 找到09:30:00的开盘价（当日第一根分钟线）
                target_bars = current_price[
                    (current_price.index.hour == 9) & 
                    (current_price.index.minute == 30)
                ]
                
                if not target_bars.empty:
                    today_open = target_bars.iloc[0]['open']
                    return today_open
                
                # 如果没有找到09:30:00的数据，继续重试
                time.sleep(self.RETRY_INTERVAL)
                
            except Exception as e:
                tqdm.write(f"获取 {stock_code} 开盘价失败(第{attempt+1}次): {str(e)}")
                time.sleep(self.RETRY_INTERVAL)
                continue
        
        return None
    
    def _wait_for_market_open(self):
        """
        等待市场开盘（09:30）
        
        在获取开盘价前确保市场已经开盘，避免获取不到09:30的数据
        """
        if self.dry_run:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 模拟模式：跳过等待开盘")
            return
        
        target_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        
        if datetime.now() < target_time:
            wait_seconds = (target_time - datetime.now()).total_seconds()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 等待市场开盘...")
            print(f"预计等待时间: {int(wait_seconds)} 秒")
            
            for _ in tqdm(range(int(wait_seconds)), desc="等待市场开盘"):
                time.sleep(1)
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 市场已开盘，开始获取开盘价...")
    
    def _filter_high_open_stocks(self) -> list:
        """
        筛选高开2个点以上的股票
        
        Returns:
            高开股票列表，包含代码、昨收、今开、高开幅度
        """
        open_high_2pct_stocks = []
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始筛选高开股票...")
        print(f"待检查股票数量: {len(self.limit_up_codes)}")
        
        for stock in tqdm(self.limit_up_codes, desc="筛选高开股票"):
            try:
                # stock_code = self._get_stock_code_with_prefix(stock)
                stock_code = add_exchange_prefix(stock, sep='')
                # price = get_price_pro(stock_code, start_date, end_date)
                
                df_day = self.code2price[stock].sort_index(ascending=True)
                yesterday_close = df_day.iloc[-1]['close']
                
                today_open = self._get_opening_price(stock_code)
                
                if today_open is None:
                    tqdm.write(f"无法获取 {stock} 开盘价")
                    continue
                
                if today_open / yesterday_close >= self.OPEN_UP_THRESH:
                    open_pct = round((today_open / yesterday_close - 1) * 100, 2)
                    open_high_2pct_stocks.append({
                        'code': stock,
                        'yesterday_close': round(yesterday_close, 2),
                        'today_real_open': round(today_open, 2),
                        'open_pct': open_pct
                    })
                
                time.sleep(0.05)
                
            except Exception as e:
                tqdm.write(f"处理 {stock} 失败: {str(e)}")
                continue
        
        return open_high_2pct_stocks
    
    def _wait_for_auction(self):
        """
        等待竞价结束（9:25）
        
        竞价结束时间是9:25，但接口可能有延迟，这里等待到9:26再开始获取数据
        """
        if self.dry_run:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 模拟模式：跳过等待竞价")
            return
        
        target_time = datetime.now().replace(hour=9, minute=26, second=0, microsecond=0)
        
        if datetime.now() < target_time:
            wait_seconds = (target_time - datetime.now()).total_seconds()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 等待竞价结束...")
            print(f"预计等待时间: {int(wait_seconds)} 秒")
            
            for _ in tqdm(range(int(wait_seconds)), desc="等待竞价结束"):
                time.sleep(1)
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 竞价结束，开始获取开盘价...")
    
    def _save_results(self, results: list):
        """
        保存结果到JSON文件
        
        Args:
            results: 高开股票列表
        """
        result_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'task_name': self.task_name,
            'limit_up_count': len(self.limit_up_codes),
            'limit_up_codes': self.limit_up_codes,
            'high_open_count': len(results),
            'results': results
        }
        
        filename = f"high_open_2pct_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {filepath}")
        return filepath
    
    def _output_results(self, results: list):
        """
        输出最终结果
        
        Args:
            results: 高开股票列表
        """
        print(f"\n{'='*70}")
        print(f"===== 连续2日涨停 + 当日高开2个点以上个股 =====")
        print(f"日期: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"模式: {'模拟运行' if self.dry_run else '实盘运行'}")
        print(f"筛选数量: {len(results)}")
        print(f"{'='*70}")
        
        if results:
            for item in results:
                print(f"股票:{item['code']} 昨收:{item['yesterday_close']} 今开:{item['today_real_open']} 高开幅度:{item['open_pct']}%")
        else:
            print("无符合条件的股票")
        
        print(f"{'='*70}\n")
    
    def run(self):
        """
        执行任务的完整流程
        """
        if not ASHARE_AVAILABLE:
            print("错误：Ashare库未安装")
            return
        
        # 阶段1: 获取股票代码和日线数据
        print(f"\n{'='*60}")
        print("阶段1: 获取股票列表和日线数据")
        print(f"{'='*60}")
        
        try:
            total_codes = get_stock_codes()
            print(f"获取到 {len(total_codes)} 只股票代码")
        except Exception as e:
            print(f"获取股票代码失败: {str(e)}")
            return
        
        # 阶段2: 获取日线数据并筛选连板股票
        print(f"\n{'='*60}")
        print("阶段2: 筛选连续两日涨停股票")
        print(f"{'='*60}")
        
        self.code2price = self._fetch_daily_data(total_codes)
        
        if not self.code2price:
            print("警告：未获取到任何股票数据")
            return
        
        self.limit_up_codes = self._filter_limit_up_codes(self.code2price)
        
        if not self.limit_up_codes:
            print("警告：未找到连续涨停股票")
            return
        
        print(f"\n连续涨停股票列表: {self.limit_up_codes}")
        
        # 阶段3: 等待竞价结束
        print(f"\n{'='*60}")
        print("阶段3: 等待竞价结束")
        print(f"{'='*60}")
        
        self._wait_for_auction()
        
        # 阶段4: 等待市场开盘
        print(f"\n{'='*60}")
        print("阶段4: 等待市场开盘")
        print(f"{'='*60}")
        
        self._wait_for_market_open()
        
        # 阶段5: 获取开盘价并筛选高开股票
        print(f"\n{'='*60}")
        print("阶段5: 筛选高开2个点以上股票")
        print(f"{'='*60}")
        
        results = self._filter_high_open_stocks()
        
        # 阶段6: 保存并输出结果
        self._save_results(results)
        self._output_results(results)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='连续涨停高开2点策略')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行模式（跳过等待竞价）')
    args = parser.parse_args()
    args.dry_run = True
    task = HighOpen2PctTask(dry_run=args.dry_run)
    task.execute()