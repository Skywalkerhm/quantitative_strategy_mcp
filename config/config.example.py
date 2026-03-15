# Quantitative Strategy MCP - Configuration Example
# Copy this file to config.py and modify as needed

# Database path (REQUIRED - change to your database location)
DB_PATH = "/path/to/your/stock_database.db"

# Default parameters
DEFAULT_MARKET = "A"  # 'A' for A-shares, 'HK' for HK shares, 'US' for US stocks
DEFAULT_THRESHOLD = 0.02  # 2% threshold for alerts
DEFAULT_LOOKBACK = 20  # Default lookback period for factors

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/quant_mcp.log"

# MCP Server settings
MCP_SERVER_NAME = "quantitative-strategy"
MCP_SERVER_VERSION = "1.0.0"
