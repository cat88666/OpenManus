#!/bin/bash

# 远程项目承包分包平台 - 停止脚本

echo "🛑 停止远程项目承包分包平台..."
echo "=================================="

# 停止后端API
echo "🛑 停止后端API..."
pkill -f "uvicorn commercial_api" || echo "后端API未运行"

# 停止仪表板
echo "🛑 停止仪表板..."
pkill -f "streamlit run commercial_dashboard" || echo "仪表板未运行"

# 等待进程终止
sleep 2

echo "✅ 所有服务已停止"
echo ""
echo "📝 日志文件位置："
echo "  - /tmp/commercial_platform/backend.log"
echo "  - /tmp/commercial_platform/dashboard.log"
echo ""
echo "🚀 重新启动："
echo "  bash /home/ubuntu/OpenManus/scripts/start_commercial.sh"
