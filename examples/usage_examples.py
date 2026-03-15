"""
Quantitative Strategy MCP - Usage Examples

This file demonstrates how to use the MCP tools for quantitative trading.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_tools import call_mcp_tool, list_all_tools

# Set your database path
os.environ['DB_PATH'] = '/path/to/your/stock_database.db'


def example_1_get_data():
    """Example 1: Get stock data"""
    print("="*60)
    print("Example 1: Get Stock Data")
    print("="*60)
    
    result = call_mcp_tool(
        'get_stock_data',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20241231'
    )
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   First record: {result['data'][0]}")
    else:
        print(f"❌ {result['message']}")


def example_2_calculate_factor():
    """Example 2: Calculate RSI factor"""
    print("\n" + "="*60)
    print("Example 2: Calculate RSI Factor")
    print("="*60)
    
    # First get data
    data_result = call_mcp_tool(
        'get_stock_data',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20241231'
    )
    
    if not data_result['success']:
        print(f"❌ Failed to get data: {data_result['message']}")
        return
    
    # Calculate RSI
    factor_result = call_mcp_tool(
        'calculate_factor',
        data=data_result['data'],
        factor_type='rsi',
        params={'period': 14}
    )
    
    if factor_result['success']:
        print(f"✅ {factor_result['message']}")
        print(f"   Latest RSI: {factor_result['factor_values'][-1]:.2f}")
    else:
        print(f"❌ {factor_result['message']}")


def example_3_backtest():
    """Example 3: Run backtest"""
    print("\n" + "="*60)
    print("Example 3: Run Momentum Strategy Backtest")
    print("="*60)
    
    result = call_mcp_tool(
        'run_backtest',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20241231',
        strategy_type='momentum',
        params={'lookback': 20, 'threshold': 0.02}
    )
    
    if result['success']:
        print(f"✅ {result['message']}")
        metrics = result['metrics']
        print(f"   Total Return: {metrics['total_return']*100:.1f}%")
        print(f"   Annual Return: {metrics['annual_return']*100:.1f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {metrics['max_drawdown']*100:.1f}%")
        print(f"   Win Rate: {metrics['win_rate']*100:.1f}%")
    else:
        print(f"❌ {result['message']}")


def example_4_monitor():
    """Example 4: Monitor stocks"""
    print("\n" + "="*60)
    print("Example 4: Monitor Stock Prices")
    print("="*60)
    
    result = call_mcp_tool(
        'monitor_stocks',
        stock_list=['000001.SZ', '000002.SZ', '600036.SH'],
        threshold=0.03  # 3% threshold
    )
    
    if result['success']:
        print(f"✅ {result['message']}")
        if result['alerts']:
            print("\n   Alerts:")
            for alert in result['alerts']:
                print(f"   ⚠️  {alert['message']}")
        else:
            print("   No alerts")
    else:
        print(f"❌ {result['message']}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Quantitative Strategy MCP - Examples")
    print("="*60)
    
    # List available tools
    print("\n" + list_all_tools())
    
    # Run examples
    example_1_get_data()
    example_2_calculate_factor()
    example_3_backtest()
    example_4_monitor()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
