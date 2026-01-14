#!/bin/bash

# 远程项目承包分包平台 - 一键启动脚本

set -e

echo "🚀 远程项目承包分包平台 - 启动脚本"
echo "=================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3 已安装"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装"
    exit 1
fi

echo "✅ pip3 已安装"

# 项目根目录
PROJECT_ROOT="/home/ubuntu/OpenManus"
BACKEND_DIR="$PROJECT_ROOT/platform/backend"
DASHBOARD_DIR="$PROJECT_ROOT/platform/streamlit-dashboard"

echo ""
echo "📦 安装依赖..."
echo "=================================="

# 安装后端依赖
echo "📦 安装后端依赖..."
cd "$BACKEND_DIR"
pip install -q -r requirements.txt 2>/dev/null || true
pip install -q fastapi uvicorn selenium beautifulsoup4 aiohttp 2>/dev/null || true

# 安装仪表板依赖
echo "📦 安装仪表板依赖..."
cd "$DASHBOARD_DIR"
pip install -q streamlit pandas plotly requests 2>/dev/null || true

echo "✅ 依赖安装完成"

echo ""
echo "🚀 启动服务..."
echo "=================================="

# 创建日志目录
mkdir -p /tmp/commercial_platform

# 启动后端API
echo "🚀 启动后端API (端口 8000)..."
cd "$BACKEND_DIR"
nohup python -m uvicorn commercial_api:app --host 0.0.0.0 --port 8000 > /tmp/commercial_platform/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端API已启动 (PID: $BACKEND_PID)"

# 等待API启动
sleep 3

# 检查API是否运行
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API 健康检查通过"
else
    echo "⚠️  API 可能未完全启动，请稍候..."
fi

# 启动仪表板
echo "🚀 启动仪表板 (端口 8501)..."
cd "$DASHBOARD_DIR"
nohup streamlit run commercial_dashboard.py --server.port=8501 --server.address=0.0.0.0 > /tmp/commercial_platform/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "✅ 仪表板已启动 (PID: $DASHBOARD_PID)"

echo ""
echo "✅ 所有服务已启动！"
echo "=================================="
echo ""
echo "📍 访问地址："
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 仪表板: http://localhost:8501"
echo ""
echo "📝 日志文件："
echo "  - 后端日志: /tmp/commercial_platform/backend.log"
echo "  - 仪表板日志: /tmp/commercial_platform/dashboard.log"
echo ""
echo "🛑 停止服务："
echo "  bash $PROJECT_ROOT/scripts/stop_commercial.sh"
echo ""
echo "📚 快速开始指南："
echo "  cat $PROJECT_ROOT/QUICK_START_COMMERCIAL.md"
echo ""
echo "🎉 系统已准备好！现在可以开始添加团队成员和项目了！"
echo ""

# 保存PID
echo "$BACKEND_PID" > /tmp/commercial_platform/backend.pid
echo "$DASHBOARD_PID" > /tmp/commercial_platform/dashboard.pid

# 显示实时日志
echo "📋 实时日志 (按 Ctrl+C 停止)："
echo "=================================="
tail -f /tmp/commercial_platform/backend.log &
TAIL_PID=$!

# 等待中断信号
trap "kill $TAIL_PID 2>/dev/null; exit 0" SIGINT

wait
