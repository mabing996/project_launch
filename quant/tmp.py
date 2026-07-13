import pandas as pd
import numpy as np
from util import load_local_daily_data,get_limit_type,get_basic_info_pro,filter_st_codes,calculate_max_drawdown
def pick_stocks(stock_data, day_num_before=0):
    """
    选股函数
    条件：
    1. limit_type为10%涨跌幅标的
    2. 今日收盘价站上5日均线，5日均线大于10日均线，10日均线大于20日均线
    3. 最新收盘价低于历史最高价0.5倍
    参数:
        stock_data: dict，key为股票代码（如 '600000.SH'），value为DataFrame
                    DataFrame包含以下列: open, high, low, close, volume, pct_chg, turnover_rate, volume_ratio
    返回:
        list，选中的股票代码列表
    """
    selected = []
    print(f"总股票数: {len(stock_data)}")
    for code, df in stock_data.items():


        ori_df = df.copy()
        if day_num_before <= 0:
            df = df.copy()
        else:
            df = df.copy().iloc[:-day_num_before]
        if df.empty or len(df) < 20:
            continue
        # 过滤只保留10%涨跌幅个股
        code_num = code.split('.')[0]
        limit_type = get_limit_type(code_num)
        if limit_type != 10:
            continue
        
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma10"] = df["close"].rolling(10).mean()
        df["ma20"] = df["close"].rolling(20).mean()
        latest = df.iloc[-1]
        close = latest["close"]
        ma5 = latest["ma5"]
        ma10 = latest["ma10"]
        ma20 = latest["ma20"]

        df['ma5_10'] = df['ma5'] >= df['ma10']
        df['ma10_20'] = df['ma10'] >= df['ma20']
        df['ma5_20'] = df['ma5'] >= df['ma20']
        
        df['max_drawdown_5'] = calculate_max_drawdown(df['high'], df['low'], window=5)
        df['max_drawdown_10'] = calculate_max_drawdown(df['high'], df['low'], window=10)
        df['max_drawdown_20'] = calculate_max_drawdown(df['high'], df['low'], window=20)

        EMA_DAY = 20        
        RATIO_THRESH = 0.8  # 占比阈值80%
        # print('debug')
        # 1. 标记每日：5日EMA > 20日EMA 为True
        df['ma5_20'] = df['ma5'] >= df['ma20']
        # 2. 滚动20天，计算满足条件的天数占比
        df['ma5_above_ratio'] = df['ma5_20'].rolling(window=EMA_DAY).sum() / EMA_DAY

        df['ma10_20'] = df['ma10'] >= df['ma20']
        df['ma10_above_ratio'] = df['ma10_20'].rolling(window=EMA_DAY).sum() / EMA_DAY

        # 均线非空、收盘价站上5日线、5>10、10>20

        latest = df.iloc[-1]
        close = latest["close"]
        ma5 = latest["ma5"]
        ma10 = latest["ma10"]
        ma20 = latest["ma20"]
        # 取当日最新滚动占比数值
        ma5_above_ratio = latest["ma5_above_ratio"]
        ma10_above_ratio = latest["ma10_above_ratio"]  
        max_drawdown_10 = latest["max_drawdown_10"]
        max_drawdown_20 = latest["max_drawdown_20"]

        # 基础均线多头条件
        # if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
        #     continue
        # if close < ma5 or ma5 <= ma10 or ma10 <= ma20:
        #     continue
        # 20日占比条件
        if pd.isna(ma5_above_ratio) or ma5_above_ratio < RATIO_THRESH:
            continue
        if pd.isna(ma10_above_ratio) or ma10_above_ratio < RATIO_THRESH:
            continue
        if close < ma20 or close < ma10:
            continue
        if max_drawdown_10 > 0.1:
            continue

        if max_drawdown_20 > 0.1:
            continue
        
        max_high = df["high"].max()
        # if 1.5 * close >= max_high :
        #     continue

        up_ratio = round(max_high / close - 1, 2)
        print(f"选中: {code}, 买入价格{close:.2f}, MA5:{ma5:.2f}, MA10:{ma10:.2f}, MA20:{ma20:.2f}, 历史最高{max_high:.2f}, 最新价格:{ori_df.iloc[-1]['close']:.2f} up_ratio:{up_ratio:.2f}")
        selected.append(code)
    print(f"共选出 {len(selected)} 只股票")
    return selected


if __name__ == '__main__':
    stock_data = load_local_daily_data()
    day = 0
    selected = pick_stocks(stock_data, day_num_before=day)
    tmp_codes = stock_data['603629.SH']
    last_date = tmp_codes.iloc[-1].name
    last_date = last_date.strftime('%Y%m%d')
    for code in selected:
        name, industry, pe, pe_ttm, pb, total_mv = get_basic_info_pro(code, last_date)
        print(f"{code}, {name}, {industry}, {pe}, {pe_ttm}, {pb}, {total_mv}")
    print(f'last_date={last_date}')
    # print(selected)
    # selected = pick_stocks(stock_data, day_num_before=10)
    # tmp_codes = stock_data['603629.SH']
    # for day in range(10, 21):
    #     selected = pick_stocks(stock_data, day_num_before=day)
    #     date = tmp_codes.iloc[-(day+1)].name
    #     print(f"day={day}, 选中股票数: {len(selected)}, 日期: {date}")

    print('done')
