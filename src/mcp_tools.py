"""
MCP 工具封装 - 量化策略系统

基于 ClawHub FinStep MCP 和 Stock Monitor Skill 的学习
将现有功能封装为标准化工具，供 LLM 调用

作者：马上有钱
日期：2026-03-15
版本：1.0.0
"""

import numpy as np
import pandas as pd
import sqlite3
import os
import sys
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从环境变量或配置文件获取数据库路径
DB_PATH = os.environ.get(
    'DB_PATH', 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'stock_database.db')
)


# ==================== MCP 工具装饰器 ====================

class MCPToolRegistry:
    """MCP 工具注册表"""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str = None, description: str = ""):
        """注册工具函数"""
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = {
                'function': func,
                'name': tool_name,
                'description': description,
                'docstring': func.__doc__
            }
            return func
        return decorator
    
    def get_tool(self, name: str):
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [
            {
                'name': info['name'],
                'description': info['description'],
                'docstring': info['docstring']
            }
            for info in self.tools.values()
        ]
    
    def call_tool(self, name: str, **kwargs):
        """调用工具"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"工具 {name} 不存在")
        return tool['function'](**kwargs)


# 全局工具注册表
mcp_tools = MCPToolRegistry()


# ==================== 数据获取工具 ====================

@mcp_tools.register(
    name='get_stock_data',
    description='获取股票历史行情数据'
)
def get_stock_data(
    ts_code: str,
    start_date: str,
    end_date: str,
    db_path: str = None
) -> Dict:
    """
    获取股票历史行情数据
    
    参数:
        ts_code: 股票代码，如 '000001.SZ'
        start_date: 开始日期，格式 'YYYYMMDD'
        end_date: 结束日期，格式 'YYYYMMDD'
        db_path: 数据库路径 (默认从环境变量 DB_PATH 读取)
    
    返回:
        {
            'success': bool,
            'data': DataFrame (包含 open, high, low, close, vol),
            'count': int (数据条数),
            'message': str
        }
    """
    if db_path is None:
        db_path = DB_PATH
    
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT trade_date, open, high, low, close, vol 
        FROM daily 
        WHERE ts_code = '{ts_code}' 
          AND trade_date >= {start_date} 
          AND trade_date <= {end_date}
        ORDER BY trade_date
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) == 0:
            return {
                'success': False,
                'data': None,
                'count': 0,
                'message': f'未找到股票 {ts_code} 的数据'
            }
        
        return {
            'success': True,
            'data': df.to_dict('records'),
            'count': len(df),
            'message': f'成功获取 {len(df)} 条数据'
        }
    
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'count': 0,
            'message': f'获取数据失败：{str(e)}'
        }


@mcp_tools.register(
    name='get_stock_list',
    description='获取股票列表'
)
def get_stock_list(
    market: str = 'A',
    db_path: str = None
) -> Dict:
    """
    获取股票列表
    
    参数:
        market: 市场类型 ('A'股，'HK'港股，'US'美股)
        db_path: 数据库路径
    
    返回:
        {
            'success': bool,
            'stocks': List[Dict],
            'count': int
        }
    """
    if db_path is None:
        db_path = DB_PATH
    
    try:
        conn = sqlite3.connect(db_path)
        query = """
        SELECT DISTINCT ts_code, name, industry 
        FROM daily 
        WHERE ts_code LIKE ?
        LIMIT 100
        """
        
        if market == 'A':
            pattern = '%.SZ'
        elif market == 'HK':
            pattern = '%.HK'
        else:
            pattern = '%%'
        
        df = pd.read_sql_query(query, conn, params=[pattern])
        conn.close()
        
        return {
            'success': True,
            'stocks': df.to_dict('records'),
            'count': len(df)
        }
    
    except Exception as e:
        return {
            'success': False,
            'stocks': [],
            'count': 0,
            'message': str(e)
        }


# ==================== 因子计算工具 ====================

@mcp_tools.register(
    name='calculate_factor',
    description='计算量化因子'
)
def calculate_factor(
    data: Union[List[Dict], pd.DataFrame],
    factor_type: str,
    params: Dict = None
) -> Dict:
    """
    计算量化因子
    
    参数:
        data: 股票数据 (列表或 DataFrame)
        factor_type: 因子类型 ('momentum', 'rsi', 'macd', 'volatility', 'volume_ratio')
        params: 因子参数
    
    返回:
        {
            'success': bool,
            'factor_values': List[float],
            'factor_name': str,
            'message': str
        }
    """
    try:
        # 转换为 DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        if params is None:
            params = {}
        
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['vol'].values
        
        factor_values = None
        
        if factor_type == 'momentum':
            # 动量因子
            lookback = params.get('lookback', 20)
            factor_values = (close - np.roll(close, lookback)) / np.roll(close, lookback)
            factor_values[:lookback] = np.nan
        
        elif factor_type == 'rsi':
            # RSI 因子
            period = params.get('period', 14)
            delta = np.diff(close)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            
            avg_gain = np.zeros(len(close))
            avg_loss = np.zeros(len(close))
            
            avg_gain[period] = np.mean(gain[:period])
            avg_loss[period] = np.mean(loss[:period])
            
            for i in range(period + 1, len(close)):
                avg_gain[i] = (avg_gain[i-1] * (period-1) + gain[i-1]) / period
                avg_loss[i] = (avg_loss[i-1] * (period-1) + loss[i-1]) / period
            
            rs = np.zeros(len(close))
            mask = avg_loss > 0
            rs[mask] = avg_gain[mask] / avg_loss[mask]
            factor_values = 100 - (100 / (1 + rs))
            factor_values[:period] = np.nan
        
        elif factor_type == 'macd':
            # MACD 因子
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            
            ema_fast = pd.Series(close).ewm(span=fast).mean().values
            ema_slow = pd.Series(close).ewm(span=slow).mean().values
            factor_values = ema_fast - ema_slow
        
        elif factor_type == 'volatility':
            # 波动率因子
            lookback = params.get('lookback', 20)
            returns = np.diff(close) / close[:-1]
            volatility = np.zeros(len(close))
            
            for i in range(lookback, len(close)):
                volatility[i] = np.std(returns[i-lookback:i]) * np.sqrt(252)
            
            factor_values = volatility
        
        elif factor_type == 'volume_ratio':
            # 成交量比率
            lookback = params.get('lookback', 20)
            ma_volume = pd.Series(volume).rolling(window=lookback).mean().values
            factor_values = volume / (ma_volume + 1e-8)
        
        else:
            return {
                'success': False,
                'factor_values': None,
                'factor_name': factor_type,
                'message': f'不支持的因子类型：{factor_type}'
            }
        
        # 处理 NaN
        factor_values = np.nan_to_num(factor_values, nan=0.0)
        
        return {
            'success': True,
            'factor_values': factor_values.tolist(),
            'factor_name': factor_type,
            'message': f'成功计算 {factor_type} 因子'
        }
    
    except Exception as e:
        return {
            'success': False,
            'factor_values': None,
            'factor_name': factor_type,
            'message': f'计算失败：{str(e)}'
        }


# ==================== 回测工具 ====================

@mcp_tools.register(
    name='run_backtest',
    description='运行策略回测'
)
def run_backtest(
    ts_code: str,
    start_date: str,
    end_date: str,
    strategy_type: str = 'momentum',
    params: Dict = None,
    db_path: str = None
) -> Dict:
    """
    运行策略回测
    
    参数:
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        strategy_type: 策略类型 ('momentum', 'breakout', 'mean_reversion')
        params: 策略参数
        db_path: 数据库路径
    
    返回:
        {
            'success': bool,
            'metrics': Dict (年化收益、Sharpe、最大回撤等),
            'daily_returns': List[float],
            'message': str
        }
    """
    if db_path is None:
        db_path = DB_PATH
    
    try:
        # 获取数据
        data_result = get_stock_data(ts_code, start_date, end_date, db_path)
        
        if not data_result['success']:
            return data_result
        
        data = pd.DataFrame(data_result['data'])
        
        if len(data) < 60:
            return {
                'success': False,
                'metrics': None,
                'daily_returns': [],
                'message': '数据不足 60 天'
            }
        
        if params is None:
            params = {}
        
        close = data['close'].values
        n = len(close)
        
        # 生成信号
        signals = np.zeros(n)
        
        if strategy_type == 'momentum':
            lookback = params.get('lookback', 20)
            threshold = params.get('threshold', 0.02)
            
            for i in range(lookback, n):
                ret = (close[i] - close[i-lookback]) / close[i-lookback]
                if ret > threshold:
                    signals[i] = 1
                elif ret < -threshold:
                    signals[i] = -1
        
        elif strategy_type == 'breakout':
            lookback = params.get('lookback', 20)
            
            for i in range(lookback, n):
                highest = np.max(close[i-lookback:i])
                lowest = np.min(close[i-lookback:i])
                if close[i] > highest:
                    signals[i] = 1
                elif close[i] < lowest:
                    signals[i] = -1
        
        elif strategy_type == 'mean_reversion':
            lookback = params.get('lookback', 20)
            
            for i in range(lookback, n):
                ma = np.mean(close[i-lookback:i])
                std = np.std(close[i-lookback:i])
                z_score = (close[i] - ma) / (std + 1e-8)
                
                if z_score < -2:
                    signals[i] = 1  # 超卖买入
                elif z_score > 2:
                    signals[i] = -1  # 超买卖出
        
        # 计算收益
        daily_ret = np.diff(close) / close[:-1]
        strategy_ret = signals[:-1] * daily_ret
        
        # 计算指标
        total_ret = np.prod(1 + strategy_ret) - 1
        ann_ret = (1 + total_ret) ** (252 / len(strategy_ret)) - 1 if len(strategy_ret) > 0 else 0
        mean_ret = np.mean(strategy_ret)
        std_ret = np.std(strategy_ret) + 1e-8
        sharpe = np.sqrt(252) * mean_ret / std_ret
        
        # 最大回撤
        cum_ret = np.cumprod(1 + strategy_ret)
        running_max = np.maximum.accumulate(cum_ret)
        drawdown = (cum_ret - running_max) / running_max
        max_dd = np.min(drawdown)
        
        # 胜率
        win_rate = np.mean(strategy_ret > 0)
        
        metrics = {
            'total_return': float(total_ret),
            'annual_return': float(ann_ret),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd),
            'win_rate': float(win_rate),
            'total_days': len(strategy_ret),
            'strategy_type': strategy_type
        }
        
        return {
            'success': True,
            'metrics': metrics,
            'daily_returns': strategy_ret.tolist(),
            'message': f'回测完成：年化收益 {ann_ret*100:.1f}%, Sharpe {sharpe:.2f}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'metrics': None,
            'daily_returns': [],
            'message': f'回测失败：{str(e)}'
        }


# ==================== 策略评估工具 ====================

@mcp_tools.register(
    name='evaluate_strategy',
    description='评估策略表现'
)
def evaluate_strategy(
    backtest_results: List[Dict],
    benchmark_return: float = 0.0
) -> Dict:
    """
    评估策略表现
    
    参数:
        backtest_results: 回测结果列表
        benchmark_return: 基准收益
    
    返回:
        {
            'success': bool,
            'evaluation': Dict (综合评分、各维度得分),
            'message': str
        }
    """
    try:
        if len(backtest_results) == 0:
            return {
                'success': False,
                'evaluation': None,
                'message': '没有回测结果'
            }
        
        # 提取指标
        sharpe_list = [r['metrics']['sharpe_ratio'] for r in backtest_results if r['metrics']]
        return_list = [r['metrics']['annual_return'] for r in backtest_results if r['metrics']]
        dd_list = [r['metrics']['max_drawdown'] for r in backtest_results if r['metrics']]
        win_rate_list = [r['metrics']['win_rate'] for r in backtest_results if r['metrics']]
        
        if len(sharpe_list) == 0:
            return {
                'success': False,
                'evaluation': None,
                'message': '没有有效的回测结果'
            }
        
        # 各维度评分
        avg_sharpe = np.mean(sharpe_list)
        avg_return = np.mean(return_list)
        avg_dd = np.mean(dd_list)
        avg_win_rate = np.mean(win_rate_list)
        
        # 稳定性 (Sharpe 的标准差)
        sharpe_std = np.std(sharpe_list) if len(sharpe_list) > 1 else 0
        stability = 1.0 - min(1.0, sharpe_std)
        
        # 鲁棒性 (回撤控制)
        robustness = 1.0 - min(1.0, abs(avg_dd))
        
        # 综合评分
        total_score = (
            0.3 * min(1.0, avg_sharpe / 2.0) +
            0.25 * min(1.0, max(0, avg_return) / 0.3) +
            0.2 * stability +
            0.15 * robustness +
            0.1 * avg_win_rate
        )
        
        evaluation = {
            'total_score': float(total_score),
            'dimensions': {
                'predictive_power': float(min(1.0, avg_sharpe / 2.0)),
                'return': float(min(1.0, max(0, avg_return) / 0.3)),
                'stability': float(stability),
                'robustness': float(robustness),
                'win_rate': float(avg_win_rate)
            },
            'metrics': {
                'avg_sharpe': float(avg_sharpe),
                'avg_return': float(avg_return),
                'avg_drawdown': float(avg_dd),
                'avg_win_rate': float(avg_win_rate),
                'n_stocks': len(backtest_results)
            }
        }
        
        # 生成评价
        if total_score > 0.7:
            comment = "优秀策略！建议进一步实盘测试"
        elif total_score > 0.5:
            comment = "良好策略，可以优化参数后使用"
        elif total_score > 0.3:
            comment = "一般策略，需要改进"
        else:
            comment = "策略表现不佳，建议重新设计"
        
        return {
            'success': True,
            'evaluation': evaluation,
            'message': f'评估完成：综合评分 {total_score:.3f} - {comment}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'evaluation': None,
            'message': f'评估失败：{str(e)}'
        }


# ==================== 股票监控工具 ====================

@mcp_tools.register(
    name='monitor_stocks',
    description='监控股票价格变化'
)
def monitor_stocks(
    stock_list: List[str],
    threshold: float = 0.02,
    db_path: str = None
) -> Dict:
    """
    监控股票价格变化
    
    参数:
        stock_list: 股票代码列表
        threshold: 预警阈值 (默认 2%)
        db_path: 数据库路径
    
    返回:
        {
            'success': bool,
            'alerts': List[Dict] (预警信息),
            'current_prices': Dict,
            'message': str
        }
    """
    if db_path is None:
        db_path = DB_PATH
    
    try:
        alerts = []
        current_prices = {}
        
        # 获取最新数据
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        for ts_code in stock_list:
            # 获取最新价格
            conn = sqlite3.connect(db_path)
            query = f"""
            SELECT trade_date, close 
            FROM daily 
            WHERE ts_code = '{ts_code}'
            ORDER BY trade_date DESC 
            LIMIT 2
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) < 2:
                continue
            
            current_price = df.iloc[0]['close']
            prev_price = df.iloc[1]['close']
            
            current_prices[ts_code] = current_price
            
            # 计算涨跌幅
            change_pct = (current_price - prev_price) / prev_price
            
            # 检查预警
            if abs(change_pct) > threshold:
                alerts.append({
                    'ts_code': ts_code,
                    'current_price': float(current_price),
                    'change_pct': float(change_pct),
                    'direction': 'up' if change_pct > 0 else 'down',
                    'message': f"{ts_code} 涨跌幅 {change_pct*100:.2f}% 超过阈值 {threshold*100:.1f}%"
                })
        
        return {
            'success': True,
            'alerts': alerts,
            'current_prices': current_prices,
            'message': f'监控完成：发现 {len(alerts)} 个预警'
        }
    
    except Exception as e:
        return {
            'success': False,
            'alerts': [],
            'current_prices': {},
            'message': f'监控失败：{str(e)}'
        }


# ==================== 工具列表和调用接口 ====================

def list_all_tools() -> str:
    """列出所有可用工具"""
    tools = mcp_tools.list_tools()
    
    output = "=== MCP 工具列表 ===\n\n"
    for i, tool in enumerate(tools, 1):
        output += f"{i}. **{tool['name']}**\n"
        output += f"   描述：{tool['description']}\n"
        output += f"   文档：{tool['docstring'][:200]}...\n\n"
    
    return output


def call_mcp_tool(tool_name: str, **kwargs) -> Dict:
    """调用 MCP 工具的统一接口"""
    return mcp_tools.call_tool(tool_name, **kwargs)


# ==================== 主函数 (演示) ====================

if __name__ == '__main__':
    print("=" * 70)
    print("MCP 工具封装演示")
    print("=" * 70)
    
    # 列出所有工具
    print("\n" + list_all_tools())
    
    # 演示 1: 获取股票数据
    print("\n【演示 1】获取股票数据")
    result = call_mcp_tool(
        'get_stock_data',
        ts_code='000001.SZ',
        start_date='20260101',
        end_date='20260313'
    )
    print(f"结果：{result['message']}")
    if result['success']:
        print(f"数据条数：{result['count']}")
    
    # 演示 2: 计算因子
    print("\n【演示 2】计算 RSI 因子")
    if result['success']:
        factor_result = call_mcp_tool(
            'calculate_factor',
            data=result['data'],
            factor_type='rsi',
            params={'period': 14}
        )
        print(f"结果：{factor_result['message']}")
        if factor_result['success']:
            print(f"最新 RSI: {factor_result['factor_values'][-1]:.2f}")
    
    # 演示 3: 回测
    print("\n【演示 3】回测动量策略")
    backtest_result = call_mcp_tool(
        'run_backtest',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20260313',
        strategy_type='momentum',
        params={'lookback': 20, 'threshold': 0.02}
    )
    print(f"结果：{backtest_result['message']}")
    if backtest_result['success']:
        metrics = backtest_result['metrics']
        print(f"年化收益：{metrics['annual_return']*100:.1f}%")
        print(f"Sharpe 比率：{metrics['sharpe_ratio']:.2f}")
        print(f"最大回撤：{metrics['max_drawdown']*100:.1f}%")
    
    print("\n✅ MCP 工具演示完成!")
