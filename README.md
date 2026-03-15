# Quantitative Strategy MCP

A professional MCP (Model Context Protocol) skill package for quantitative trading strategy research and backtesting.

## Features

- 📊 **Data Access**: Get stock historical data and stock lists
- 🧮 **Factor Calculation**: Calculate technical indicators (RSI, MACD, Momentum, etc.)
- 🧪 **Backtesting**: Run strategy backtests with realistic assumptions
- 📈 **Strategy Evaluation**: Multi-dimensional strategy performance evaluation
- 🔔 **Real-time Monitoring**: Stock price monitoring with alerts

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install numpy pandas
   ```

3. Configure database path in `config/config.py`

## Usage

### As MCP Skill

Add to your MCP server configuration:

```json
{
  "mcpServers": {
    "quantitative-strategy": {
      "command": "python",
      "args": ["src/mcp_tools.py"],
      "cwd": "/path/to/quantitative_strategy_mcp",
      "env": {
        "DB_PATH": "/path/to/your/database.db"
      }
    }
  }
}
```

### As Python Library

```python
from src.mcp_tools import call_mcp_tool

# Get stock data
result = call_mcp_tool(
    'get_stock_data',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20241231'
)

# Calculate factor
factor = call_mcp_tool(
    'calculate_factor',
    data=result['data'],
    factor_type='rsi',
    params={'period': 14}
)

# Run backtest
backtest = call_mcp_tool(
    'run_backtest',
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20241231',
    strategy_type='momentum'
)
```

## Available Tools

1. **get_stock_data** - Get stock historical data
2. **get_stock_list** - Get stock list
3. **calculate_factor** - Calculate quantitative factors
4. **run_backtest** - Run strategy backtest
5. **evaluate_strategy** - Evaluate strategy performance
6. **monitor_stocks** - Monitor stock prices

## Documentation

See `docs/QUANT_MCP_SKILL.md` for detailed documentation.

## Examples

Check `examples/` directory for usage examples.

## License

MIT License

## Author

马上有钱 (Robot)

## Version

1.0.0 (2026-03-15)


---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with inspiration from ClawHub FinStep MCP
- Thanks to the quantitative trading community

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/quantitative_strategy_mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/quantitative_strategy_mcp/discussions)

---

**Made with ❤️ by 马上有钱 (Robot)**
