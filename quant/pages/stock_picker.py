import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import StringIO

from util import load_local_daily_data


def load_stock_data():
    """加载本地股票数据"""
    return load_local_daily_data()


def get_default_code():
    """获取默认的选股代码模板"""
    return '''def pick_stocks(stock_data):
    """
    选股函数
    
    参数:
        stock_data: dict，key为股票代码（如 '600000.SH'），value为DataFrame
                    DataFrame包含以下列: open, high, low, close, volume, pct_chg, turnover_rate, volume_ratio
    
    返回:
        list，选中的股票代码列表
    """
    selected = []
    
    print(f"总股票数: {len(stock_data)}")
    
    for code, df in stock_data.items():
        if df.empty or len(df) < 2:
            continue
            
        recent = df.iloc[-2:]
        
        if len(recent) >= 2:
            pct_chg_1 = recent['pct_chg'].iloc[-1]
            pct_chg_2 = recent['pct_chg'].iloc[-2]
            
            code_num = code.split('.')[0]
            limit_type = get_limit_type(code_num)
            
            if limit_type == 20:
                limit = 19.8
            elif limit_type == 30:
                limit = 29.8
            else:
                limit = 9.8
            
            if pct_chg_1 >= limit and pct_chg_2 >= limit:
                print(f"选中: {code}, 连续涨停")
                selected.append(code)
    
    print(f"共选出 {len(selected)} 只股票")
    return selected
'''


def execute_code(code, stock_data):
    """执行用户编写的代码，捕获print输出，暴露util和Ashare函数"""
    import sys
    from util import (
        get_price_pro,
        get_stk_factor_pro,
        load_local_daily_data,
        save_local_daily_data,
        get_stock_codes,
        add_exchange_prefix,
        add_exchange_suffix,
        get_limit_type,
        get_basic_info_pro,
        calculate_max_drawdown
    )
    from Ashare import get_price
    
    func_globals = {
        'stock_data': stock_data,
        'pd': pd,
        'np': np,
        'get_price_pro': get_price_pro,
        'get_stk_factor_pro': get_stk_factor_pro,
        'load_local_daily_data': load_local_daily_data,
        'save_local_daily_data': save_local_daily_data,
        'get_stock_codes': get_stock_codes,
        'add_exchange_prefix': add_exchange_prefix,
        'add_exchange_suffix': add_exchange_suffix,
        'get_limit_type': get_limit_type,
        'get_basic_info_pro': get_basic_info_pro,
        'get_price': get_price,
        'calculate_max_drawdown': calculate_max_drawdown
    }
    
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        exec(code, func_globals)
        
        if 'pick_stocks' not in func_globals:
            return None, "错误：代码中必须定义 pick_stocks 函数", captured_output.getvalue()
        
        result = func_globals['pick_stocks'](stock_data)
        
        if not isinstance(result, list):
            return None, "错误：pick_stocks 函数必须返回列表", captured_output.getvalue()
        
        return result, None, captured_output.getvalue()
        
    except Exception as e:
        return None, f"执行错误: {str(e)}", captured_output.getvalue()
    finally:
        sys.stdout = old_stdout


def main():
    st.set_page_config(page_title="量化选股", layout="wide")
    st.title("📈 量化选股平台")
    
    st.markdown("""
    在此页面编写选股策略代码，系统会自动加载本地股票数据供您使用。
    
    **使用说明：**
    1. 编写 `pick_stocks(stock_data, params)` 函数
    2. 设置自定义参数
    3. 点击执行按钮获取选股结果
    """)
    
    stock_data = load_stock_data()
    total_stocks = len(stock_data)
    
    st.info(f"📊 已加载 {total_stocks} 只股票数据")
    
    st.subheader("选股代码")
    
    st.markdown("""
    **可用函数：**
    
    | 函数名 | 说明 |
    |--------|------|
    | `get_price_pro(code, start_date, end_date)` | tushare日线数据 |
    | `get_stk_factor_pro(ts_code/trade_date, ...)` | tushare因子数据(带复权) |
    | `get_price(code, end_date='', count=10, frequency='1d')` | Ashare行情接口 |
    | `get_basic_info_pro(stock_code, trade_date)` | 获取股票基本信息(名称/行业/PE/PE_TTM/PB/总市值) |
    | `add_exchange_prefix(code)` | 添加交易所前缀(sh_/sz_/bj_) |
    | `add_exchange_suffix(code)` | 添加交易所后缀(.SH/.SZ/.BJ) |
    | `get_limit_type(code)` | 获取涨跌幅限制(10/20/30) |
    | `get_stock_codes()` | 获取所有股票代码 |
    | `load_local_daily_data()` | 加载本地数据 |
    """)
    
    user_code = st.text_area(
        "编写您的选股策略",
        value=get_default_code(),
        height=400,
        key='code_editor'
    )
    
    if st.button("▶️ 执行选股", key='execute_btn'):
        if not stock_data:
            st.error("❌ 没有加载到股票数据，请先运行数据下载任务")
        else:
            with st.spinner("正在执行选股策略..."):
                result, error, print_output = execute_code(user_code, stock_data)
                
                if print_output:
                    st.subheader("代码输出")
                    st.code(print_output, language='text')
                
                if error:
                    st.error(error)
                else:
                    st.success(f"✅ 选股完成，共选出 {len(result)} 只股票")
                    
                    if result:
                        st.subheader("选股结果")
                        
                        from util import get_basic_info_pro
                        import tushare as ts
                        
                        last_date = None
                        for code in result:
                            if not stock_data[code].empty:
                                last_date = stock_data[code].index[-1].strftime('%Y%m%d')
                                break
                        
                        names = []
                        industries = []
                        pes = []
                        pe_ttms = []
                        pbs = []
                        total_mvs = []
                        
                        if last_date:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            total = len(result)
                            
                            for i, code in enumerate(result):
                                status_text.text(f"正在获取股票基本信息... ({i+1}/{total})")
                                try:
                                    name, industry, pe, pe_ttm, pb, total_mv = get_basic_info_pro(code, last_date)
                                    names.append(name)
                                    industries.append(industry)
                                    pes.append(pe)
                                    pe_ttms.append(pe_ttm)
                                    pbs.append(pb)
                                    total_mvs.append(total_mv)
                                except Exception as e:
                                    names.append('')
                                    industries.append('')
                                    pes.append(0)
                                    pe_ttms.append(0)
                                    pbs.append(0)
                                    total_mvs.append(0)
                                progress_bar.progress((i + 1) / total)
                            
                            progress_bar.empty()
                            status_text.empty()
                        else:
                            names = [''] * len(result)
                            industries = [''] * len(result)
                            pes = [0] * len(result)
                            pe_ttms = [0] * len(result)
                            pbs = [0] * len(result)
                            total_mvs = [0] * len(result)
                        
                        result_df = pd.DataFrame({
                            '股票代码': [code for code in result],
                            '名称': names,
                            '同花顺': [f'<a href="https://stockpage.10jqka.com.cn/{code.split(".")[0]}/" target="_blank">查看</a>' for code in result],
                            '行业': industries,
                            '换手率(%)': [stock_data[code]['turnover_rate'].iloc[-1] if not stock_data[code].empty else 0 for code in result],
                            'PE': pes,
                            'PE_TTM': pe_ttms,
                            'PB': pbs,
                            '总市值(亿)': [mv / 10000 if mv > 0 else 0 for mv in total_mvs],
                            '最新日期': [stock_data[code].index[-1].strftime('%Y-%m-%d') if not stock_data[code].empty else '' for code in result],
                            '最新价': [stock_data[code]['close'].iloc[-1] if not stock_data[code].empty else 0 for code in result],
                            '涨跌幅(%)': [stock_data[code]['pct_chg'].iloc[-1] if not stock_data[code].empty else 0 for code in result],
                            '成交量(手)': [stock_data[code]['volume'].iloc[-1] if not stock_data[code].empty else 0 for code in result],
                        })
                        
                        numeric_cols = ['换手率(%)', 'PE', 'PE_TTM', 'PB', '总市值(亿)', '最新价', '涨跌幅(%)', '成交量(手)']
                        for col in numeric_cols:
                            if col in result_df.columns:
                                result_df[col] = result_df[col].apply(lambda x: round(x, 2) if pd.notna(x) else '')
                        
                        header_html = ''.join(f'<th>{col}</th>' for col in result_df.columns)
                        rows_html = []
                        for _, row in result_df.iterrows():
                            cells = ''.join(f'<td>{val}</td>' for val in row)
                            rows_html.append(f'<tr>{cells}</tr>')
                        body_html = ''.join(rows_html)
                        
                        html_table = f"""
                        <style>
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        th, td {{
                            padding: 8px 12px;
                            text-align: left;
                            border: 1px solid #e5e7eb;
                            white-space: nowrap;
                        }}
                        th {{
                            background-color: #f3f4f6;
                            font-weight: bold;
                        }}
                        </style>
                        <table>
                        <thead>
                        <tr>{header_html}</tr>
                        </thead>
                        <tbody>
                        {body_html}
                        </tbody>
                        </table>
                        """
                        st.markdown(html_table, unsafe_allow_html=True)
                        
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="📥 下载结果",
                            data=csv,
                            file_name=f"selected_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("📭 没有选出符合条件的股票")


if __name__ == "__main__":
    main()