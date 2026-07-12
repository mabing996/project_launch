import akshare as ak
import os
import pickle
from tqdm import tqdm


pro = None
def get_pro():
    global pro
    if pro is None:
        import tushare as ts
        # token秘钥（把给咱们的token复制过来哈）
        token = 'bc563fb9681989a2dcdd74af2bdc8bac257acbb8836db5eecd4fa949589b'
        pro = ts.pro_api(token)
        pro._DataApi__token = token  # 保证有这个代码，不然不可以获取
        # pro._DataApi__http_url = 'http://jiaoch.site'  # 保证有这个代码，不然不可以获取
        pro._DataApi__http_url = 'http://129.211.18.88:5000' 
# 测试接口(换成自己的接口）

    return pro
pro = get_pro()


def get_price_pro(stock_code: str, start_date: str, end_date: str, adj: str = 'qfq'):
    df = pro.daily(symbol=stock_code, start_date=start_date, end_date=end_date, adj=adj)
    df.sort_values(by='trade_date', inplace=True)
    return df

def get_basic_info_pro(stock_code: str, last_trade_date: str):
    """
    获取股票的基本信息（名称、行业、PE、PE_TTM、PB、总市值）
    
    Args:
        stock_code: 股票代码，格式如 '603629.SH'
        last_trade_date: 最近交易日期（不是当天，格式为yyyyMMdd，例如20260710）
    
    Returns:
        包含股票基本信息的元组，顺序为：(名称, 行业, PE, PE_TTM, PB, 总市值)

    """

    df = pro.query('stock_basic', ts_code=stock_code, list_status='L', fields='name,industry')
    name = df.iloc[0]['name']
    industry = df.iloc[0]['industry']
    df = pro.daily_basic(ts_code=stock_code, trade_date=last_trade_date, fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,total_mv')
    pe = df.iloc[0]['pe']
    pe_ttm = df.iloc[0]['pe_ttm']
    pb = df.iloc[0]['pb']
    total_mv = df.iloc[0]['total_mv']
    return name, industry, pe, pe_ttm, pb, total_mv 


def get_stk_factor_pro(ts_code: str = None, trade_date: str = None, start_date: str = None, end_date: str = None):
    """
    使用tushare的stk_factor_pro接口获取股票因子数据（带复权）
    
    支持两种查询模式：
    1. 按股票代码查询：指定 ts_code + start_date + end_date
    2. 按日期查询：指定 trade_date（获取当天所有股票数据）
    
    Args:
        ts_code: 股票代码，格式如 '603629.SH'
        trade_date: 交易日期，格式如 '20260704'
        start_date: 开始日期，格式如 '20260701'
        end_date: 结束日期，格式如 '20260707'
    
    Returns:
        包含复权价格的数据DataFrame
    """
    params = {}
    if ts_code:
        params['ts_code'] = ts_code
    if trade_date:
        params['trade_date'] = trade_date
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    df = pro.stk_factor_pro(
        **params,
        fields='ts_code,trade_date,open_qfq,close_qfq,high_qfq,low_qfq,pct_chg,vol,turnover_rate_f,volume_ratio'
    )
    df.sort_values(by='trade_date', inplace=True)
    return df


def load_local_daily_data(data_path: str = None) -> dict:
    """
    从本地加载日线数据
    
    Args:
        data_path: 数据文件路径，如果为None使用默认路径
    
    Returns:
        股票数据字典 {code: DataFrame}，如果文件不存在返回空字典
    """
    if data_path is None:
        data_dir = os.path.join(
            os.path.dirname(__file__),
            'data'
        )
        data_path = os.path.join(data_dir, 'daily_data.pkl')
    
    if os.path.exists(data_path):
        try:
            with open(data_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"加载本地数据失败: {str(e)}")
    
    return {}


def save_local_daily_data(data: dict, data_path: str = None):
    """
    保存日线数据到本地
    
    Args:
        data: 股票数据字典 {code: DataFrame}
        data_path: 数据文件路径，如果为None使用默认路径
    """
    if data_path is None:
        data_dir = os.path.join(
            os.path.dirname(__file__),
            'data'
        )
        os.makedirs(data_dir, exist_ok=True)
        data_path = os.path.join(data_dir, 'daily_data.pkl')
    
    with open(data_path, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def get_stock_codes():
    codes_df = ak.stock_info_a_code_name()
    code2name = dict(zip(codes_df['code'], codes_df['name']))
    total_codes = codes_df['code'].tolist()
    total_codes = filter_by_limit(total_codes)
    print(f'filter by limit len : {len(total_codes)}')
    # new_total_codes = []
    # for code in tqdm(total_codes):
    #     code = filter_st_codes(code, codes_df)
    #     if code:
    #         new_total_codes.append(code)
    # print(f'filter by st len : {len(new_total_codes)}')
    # total_codes = new_total_codes
    return total_codes



def get_limit_type(code: str):
    """
    返回涨跌幅类型
    10 = 10% 涨跌幅
    20 = 20% 涨跌幅
    30 = 30% 北交所
    None = 未知
    """
    code = str(code).strip()
    
    if code.startswith(('sh_', 'sz_', 'bj_')):
        code = code.split('_')[1]
    
    if not code.isdigit():
        return None
    
    # 10%: 沪深主板
    if code.startswith(('600', '601', '603', '605',
                       '000', '001', '002', '003')):
        return 10
    
    # 20%: 创业板、科创板
    elif code.startswith(('300', '301', '688')):
        return 20
    
    # 30%: 北交所
    elif code.startswith(('83', '87', '88', '92')):
        return 30
    
    return None

def filter_by_limit(codes: list, limits = [10]):
    """
    按涨跌幅限制筛选股票代码
    :param codes: 股票代码列表（可带/不带前缀）
    :param limits: 10 / 20 / 30
    :return: 带交易所前缀的代码列表
    """
    res = []
    for code in codes:
        # prefixed = add_exchange_prefix(code)
        lt = get_limit_type(code)
        
        if lt in limits:
            res.append(code)
    return res

def is_st_stock(stock_name):
    """
    判断是否为 ST、*ST 股票
    返回 True = 风险股 → 过滤掉
    """
    if not stock_name:
        return False
    
    name = str(stock_name).upper()
    return name.startswith('ST') or name.startswith('*ST') or name.startswith('SST')
def filter_st_codes(code, codes_df):
    """
    过滤出股票代码
    """
    row = codes_df[codes_df['code'] == code]
    if row.empty:
        return None
    
    stock_name = row['name'].values[0]
    if is_st_stock(stock_name):
        return None
    
    return code

def add_exchange_prefix(code: str, sep: str = '_') -> str:
    """
    根据股票代码判断交易所并添加前缀
    sh_ : 上交所（600/601/603/605/688）
    sz_ : 深交所（000/001/002/003/300/301）
    bj_ : 北交所（83/87/88/92开头）
    """
    code = str(code).strip()
    
    if not code.isdigit():
        return code  # 非数字原样返回
    
    # 北交所
    if code.startswith(('83', '87', '88', '92')):
        return f'bj{sep}{code}'
    # 上交所
    elif code.startswith(('600', '601', '603', '605', '688')):
        return f'sh{sep}{code}'
    # 深交所主板、创业板
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f'sz{sep}{code}'
    else:
        return code


def add_exchange_suffix(code: str, sep: str = '.') -> str:
    """
    根据股票代码判断交易所并添加后缀
    sh_ : 上交所（600/601/603/605/688）
    sz_ : 深交所（000/001/002/003/300/301）
    bj_ : 北交所（83/87/88/92开头）
    """
    code = str(code).strip()
    
    if not code.isdigit():
        return code  # 非数字原样返回
    
    # 北交所
    if code.startswith(('83', '87', '88', '92')):
        return f'{code}{sep}BJ'
    # 上交所
    elif code.startswith(('600', '601', '603', '605', '688')):
        return f'{code}{sep}SH'
    # 深交所主板、创业板
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f'{code}{sep}SZ'
    else:
        return code

if __name__ == '__main__':
    stock_codes = get_stock_codes()
    print(stock_codes)