#!/bin/bash
# Package script for Quantitative Strategy MCP

echo "📦 Packaging Quantitative Strategy MCP..."

# Create tarball
cd /Volumes/agents/banana
tar -czf quantitative_strategy_mcp_v1.0.0.tar.gz     --exclude='data'     --exclude='*.db'     --exclude='logs'     --exclude='__pycache__'     --exclude='.DS_Store'     quantitative_strategy_mcp/

echo "✅ Package created: quantitative_strategy_mcp_v1.0.0.tar.gz"
echo ""
echo "📦 Package contents:"
tar -tzf quantitative_strategy_mcp_v1.0.0.tar.gz | head -20
echo "..."
echo ""
echo "📊 Package size:"
ls -lh quantitative_strategy_mcp_v1.0.0.tar.gz
