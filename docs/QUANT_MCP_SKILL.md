# Quantitative Strategy MCP Skill 文档

## 📚 概述

这是一个基于 **ClawHub MCP 协议** 的量化策略技能包，提供完整的量化投研工具链。

**技能名称**: `quantitative-strategy-mcp`  
**版本**: 1.0  
**作者**: 马上有钱  
**日期**: 2026-03-15

---

## 🛠️ 可用工具

### 1. get_stock_data - 获取股票数据

**描述**: 从数据库获取股票历史行情数据

**参数**:
```json
{
  "ts_code": "股票代码，如 '000001.SZ'",
  "start_date": "开始日期 'YYYYMMDD'",
  "end_date": "结束日期 'YYYYMMDD'",
  "db_path": "数据库路径 (可选)"
}
```

**返回**:
```json
{
  "success": true,
  "data": [{"trade_date": "20260101", "open": 10.5, "high": 11.0, "low": 10.3, "close": 10.8, "vol": 1000000}],
  "count": 100,
  "message": "成功获取 100 条数据"
}
```

**使用示例**:
```
"获取平安银行 2024 年 1 月到 2026 年 3 月的行情数据"
→ 调用：get_stock_data(ts_code='000001.SZ', start_date='20240101', end_date='20260313')
```

---

### 2. get_stock_list - 获取股票列表

**描述**: 获取 A 股/港股/美股的股票列表

**参数**:
```json
{
  "market": "市场类型 ('A', 'HK', 'US')",
  "db_path": "数据库路径 (可选)"
}
```

**返回**:
```json
{
  "success": true,
  "stocks": [
    {"ts_code": "000001.SZ", "name": "平安银行", "industry": "银行"},
    {"ts_code": "000002.SZ", "name": "万科 A", "industry": "房地产"}
  ],
  "count": 100
}
```

**使用示例**:
```
"获取 A 股股票列表"
→ 调用：get_stock_list(market='A')
```

---

### 3. calculate_factor - 计算量化因子

**描述**: 计算各种量化因子 (动量、RSI、MACD、波动率等)

**参数**:
```json
{
  "data": "股票数据 (列表或 DataFrame)",
  "factor_type": "因子类型",
  "params": "因子参数 (可选)"
}
```

**支持的因子类型**:
- `momentum`: 动量因子 (参数：lookback)
- `rsi`: RSI 指标 (参数：period)
- `macd`: MACD 指标 (参数：fast, slow, signal)
- `volatility`: 波动率 (参数：lookback)
- `volume_ratio`: 成交量比率 (参数：lookback)

**返回**:
```json
{
  "success": true,
  "factor_values": [0.5, 0.6, 0.7, ...],
  "factor_name": "rsi",
  "message": "成功计算 rsi 因子"
}
```

**使用示例**:
```
"计算这个股票的 14 日 RSI 指标"
→ 调用：calculate_factor(data=stock_data, factor_type='rsi', params={'period': 14})
```

---

### 4. run_backtest - 运行策略回测

**描述**: 对指定股票运行策略回测

**参数**:
```json
{
  "ts_code": "股票代码",
  "start_date": "开始日期",
  "end_date": "结束日期",
  "strategy_type": "策略类型",
  "params": "策略参数 (可选)",
  "db_path": "数据库路径 (可选)"
}
```

**支持的策略类型**:
- `momentum`: 动量策略 (参数：lookback, threshold)
- `breakout`: 突破策略 (参数：lookback)
- `mean_reversion`: 均值回归 (参数：lookback)

**返回**:
```json
{
  "success": true,
  "metrics": {
    "total_return": 0.15,
    "annual_return": 0.12,
    "sharpe_ratio": 0.85,
    "max_drawdown": -0.18,
    "win_rate": 0.55,
    "total_days": 250
  },
  "daily_returns": [0.01, -0.005, 0.02, ...],
  "message": "回测完成：年化收益 12.0%, Sharpe 0.85"
}
```

**使用示例**:
```
"回测平安银行的动量策略，回看 20 天，阈值 2%"
→ 调用：run_backtest(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20260313',
    strategy_type='momentum',
    params={'lookback': 20, 'threshold': 0.02}
  )
```

---

### 5. evaluate_strategy - 评估策略表现

**描述**: 对回测结果进行多维度评估

**参数**:
```json
{
  "backtest_results": "回测结果列表",
  "benchmark_return": "基准收益 (可选)"
}
```

**评估维度**:
- **预测能力** (30%): Sharpe 比率
- **收益能力** (25%): 年化收益
- **稳定性** (20%): 滚动 Sharpe 标准差
- **鲁棒性** (15%): 回撤控制
- **胜率** (10%): 交易胜率

**返回**:
```json
{
  "success": true,
  "evaluation": {
    "total_score": 0.72,
    "dimensions": {
      "predictive_power": 0.65,
      "return": 0.70,
      "stability": 0.80,
      "robustness": 0.75,
      "win_rate": 0.60
    },
    "metrics": {
      "avg_sharpe": 0.85,
      "avg_return": 0.12,
      "avg_drawdown": -0.15,
      "avg_win_rate": 0.55,
      "n_stocks": 20
    }
  },
  "message": "评估完成：综合评分 0.720 - 良好策略，可以优化参数后使用"
}
```

**使用示例**:
```
"评估这个策略在 20 只股票上的综合表现"
→ 调用：evaluate_strategy(backtest_results=results_list)
```

---

### 6. monitor_stocks - 监控股票价格

**描述**: 实时监控股票价格变化，生成预警

**参数**:
```json
{
  "stock_list": "股票代码列表",
  "threshold": "预警阈值 (默认 0.02 即 2%)",
  "db_path": "数据库路径 (可选)"
}
```

**返回**:
```json
{
  "success": true,
  "alerts": [
    {
      "ts_code": "000001.SZ",
      "current_price": 12.5,
      "change_pct": 0.035,
      "direction": "up",
      "message": "000001.SZ 涨跌幅 3.50% 超过阈值 2.0%"
    }
  ],
  "current_prices": {"000001.SZ": 12.5, "000002.SZ": 25.3},
  "message": "监控完成：发现 1 个预警"
}
```

**使用示例**:
```
"监控平安银行、万科 A、招商银行，涨幅超 3% 时提醒我"
→ 调用：monitor_stocks(
    stock_list=['000001.SZ', '000002.SZ', '600036.SH'],
    threshold=0.03
  )
```

---

## 🚀 使用流程

### 场景 1: 策略研究与回测

```
1. 用户："帮我回测一个动量策略，在平安银行上测试"

2. LLM 理解意图，调用工具:
   - get_stock_data(ts_code='000001.SZ', ...)
   - run_backtest(ts_code='000001.SZ', strategy_type='momentum', ...)

3. 返回结果:
   "回测完成：年化收益 12.5%, Sharpe 0.85, 最大回撤 -15%"
```

### 场景 2: 因子挖掘

```
1. 用户："计算这个股票的 RSI 和 MACD 指标"

2. LLM 调用工具:
   - calculate_factor(data=stock_data, factor_type='rsi', params={'period': 14})
   - calculate_factor(data=stock_data, factor_type='macd', params={'fast': 12, 'slow': 26})

3. 返回结果:
   "RSI: 52.3 (中性), MACD: 0.15 (金叉信号)"
```

### 场景 3: 策略评估

```
1. 用户："评估这个策略在银行股上的表现"

2. LLM 调用工具:
   - 对多个银行股运行回测
   - evaluate_strategy(backtest_results=results)

3. 返回结果:
   "综合评分 0.72 - 良好策略，在银行股上平均年化收益 10.5%，Sharpe 0.68"
```

### 场景 4: 实时监控

```
1. 用户："监控我的自选股，涨跌幅超 3% 时飞书通知我"

2. LLM 调用工具:
   - monitor_stocks(stock_list=user_stocks, threshold=0.03)
   - 如果有预警，发送飞书消息

3. 返回结果:
   "监控中：发现 2 只股票涨幅超 3% [飞书已推送]"
```

---

## 📋 Skill 配置

### MCP 服务器配置

```json
{
  "mcpServers": {
    "quantitative-strategy": {
      "command": "python",
      "args": ["/Volumes/agents/banana/mcp_tools.py"],
      "cwd": "/Volumes/agents/banana",
      "env": {
        "DB_PATH": "/Volumes/agents/banana/data/stock_database.db"
      }
    }
  }
}
```

### OpenClaw 配置

```yaml
skills:
  - name: quantitative-strategy-mcp
    version: 1.0
    tools:
      - get_stock_data
      - get_stock_list
      - calculate_factor
      - run_backtest
      - evaluate_strategy
      - monitor_stocks
    
    data_sources:
      - name: stock_database
        type: sqlite
        path: /Volumes/agents/banana/data/stock_database.db
    
    notifications:
      - channel: feishu
        chat_id: oc_600b94e2b1756d66889777ddd71e5a89
```

---

## 🎯 最佳实践

### 1. 策略研究流程

```
1. 获取数据 → get_stock_data
2. 计算因子 → calculate_factor
3. 初步回测 → run_backtest
4. 多股票测试 → 循环调用 run_backtest
5. 综合评估 → evaluate_strategy
6. 参数优化 → 调整参数重新回测
7. 生成报告 → LLM 总结分析
```

### 2. 实时监控流程

```
1. 配置自选股列表
2. 设置预警阈值
3. 定时调用 monitor_stocks (每 5 分钟)
4. 检测到预警 → 发送通知
5. 生成日报 → 每日收盘后汇总
```

### 3. 因子挖掘流程

```
1. 用户描述策略想法 (自然语言)
2. LLM 理解并选择合适的因子
3. 调用 calculate_factor 计算
4. 回测验证效果
5. LLM 分析结果并提出优化建议
6. 迭代改进
```

---

## ⚠️ 注意事项

### 数据限制

- 数据库只包含 A 股日线数据
- 历史数据从 2020 年至今
- 实时数据需要额外接入 API

### 性能考虑

- 单次回测建议不超过 50 只股票
- 大数据量时分批处理
- 监控频率建议≥5 分钟/次

### 风险提示

- 回测结果不代表未来表现
- 策略需要实盘验证
- 注意过拟合风险
- 所有信号仅供参考，不构成投资建议

---

## 🔗 参考资源

- **ClawHub**: https://clawhub.ai/
- **MCP 协议**: https://modelcontextprotocol.io/
- **OpenClaw**: https://openclaw.ai/
- **FinStep MCP**: https://clawhub.ai/fa1c0n4826/finstep-mcp
- **Stock Monitor**: https://clawhub.ai/THIRTYFANG/stock-monitor-skill

---

## 📝 更新日志

### v1.0 (2026-03-15)
- ✅ 初始版本
- ✅ 实现 6 个核心 MCP 工具
- ✅ 支持数据获取、因子计算、回测、评估、监控
- ✅ 编写完整 Skill 文档

### TODO
- [ ] 接入实时行情 API
- [ ] 增加更多因子类型
- [ ] 支持多策略组合回测
- [ ] 集成 LLM 策略生成器
- [ ] 添加可视化报告生成

---

**维护者**: 马上有钱  
**联系方式**: 飞书群聊 oc_600b94e2b1756d66889777ddd71e5a89
