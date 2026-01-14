#!/bin/bash

###############################################################################
# 服务监控和自动恢复脚本
# 定期检查所有服务的运行状态，如果服务宕机则自动重启
###############################################################################

set -e

# 配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
STREAMLIT_PORT=8501
LOG_DIR="/tmp/openmanus_monitor"
MONITOR_LOG="$LOG_DIR/monitor.log"
CHECK_INTERVAL=60  # 检查间隔（秒）
MAX_RETRIES=3      # 最大重试次数

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

# 检查端口是否被监听
check_port() {
    local port=$1
    lsof -i ":$port" > /dev/null 2>&1
    return $?
}

# 获取占用端口的进程PID
get_pid_by_port() {
    local port=$1
    lsof -i ":$port" -t 2>/dev/null | head -1
}

# 检查进程是否正在运行
check_process() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
    return $?
}

# 启动后端API
start_backend() {
    log "启动后端API..."
    cd /home/ubuntu/OpenManus/platform/backend
    python3 commercial_api.py > "$LOG_DIR/backend.log" 2>&1 &
    local pid=$!
    sleep 2
    
    if check_port $BACKEND_PORT; then
        log "✅ 后端API已启动 (PID: $pid)"
        return 0
    else
        log "❌ 后端API启动失败"
        return 1
    fi
}

# 启动前端应用
start_frontend() {
    log "启动前端应用..."
    cd /home/ubuntu/OpenManus/platform/frontend
    npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    local pid=$!
    sleep 5
    
    if check_port $FRONTEND_PORT; then
        log "✅ 前端应用已启动 (PID: $pid)"
        return 0
    else
        log "❌ 前端应用启动失败"
        return 1
    fi
}

# 启动Streamlit仪表板
start_streamlit() {
    log "启动Streamlit仪表板..."
    cd /home/ubuntu/OpenManus/platform/streamlit-dashboard
    streamlit run app.py --server.port=$STREAMLIT_PORT > "$LOG_DIR/streamlit.log" 2>&1 &
    local pid=$!
    sleep 3
    
    if check_port $STREAMLIT_PORT; then
        log "✅ Streamlit仪表板已启动 (PID: $pid)"
        return 0
    else
        log "❌ Streamlit仪表板启动失败"
        return 1
    fi
}

# 重启服务
restart_service() {
    local service=$1
    local port=$2
    local start_func=$3
    
    log "检测到 $service 宕机，尝试重启..."
    
    # 杀死旧进程
    if check_port $port; then
        local pid=$(get_pid_by_port $port)
        if [ -n "$pid" ]; then
            kill -9 "$pid" 2>/dev/null || true
            log "已杀死旧进程 (PID: $pid)"
        fi
    fi
    
    # 重试启动
    local retry=0
    while [ $retry -lt $MAX_RETRIES ]; do
        if $start_func; then
            log "✅ $service 已成功重启"
            return 0
        fi
        
        retry=$((retry + 1))
        if [ $retry -lt $MAX_RETRIES ]; then
            log "⚠️ 重试启动 $service (尝试 $retry/$MAX_RETRIES)..."
            sleep 5
        fi
    done
    
    log "❌ $service 重启失败，已达最大重试次数"
    return 1
}

# 监控服务
monitor_services() {
    log "开始监控服务..."
    
    while true; do
        # 检查后端API
        if ! check_port $BACKEND_PORT; then
            restart_service "后端API" $BACKEND_PORT "start_backend"
        else
            log "✅ 后端API 正常运行"
        fi
        
        # 检查前端应用
        if ! check_port $FRONTEND_PORT; then
            restart_service "前端应用" $FRONTEND_PORT "start_frontend"
        else
            log "✅ 前端应用 正常运行"
        fi
        
        # 检查Streamlit仪表板
        if ! check_port $STREAMLIT_PORT; then
            restart_service "Streamlit仪表板" $STREAMLIT_PORT "start_streamlit"
        else
            log "✅ Streamlit仪表板 正常运行"
        fi
        
        log "---"
        sleep $CHECK_INTERVAL
    done
}

# 初始化和启动所有服务
init_and_start() {
    log "初始化并启动所有服务..."
    
    # 检查并杀死占用端口的进程
    for port in $BACKEND_PORT $FRONTEND_PORT $STREAMLIT_PORT; do
        if check_port $port; then
            local pid=$(get_pid_by_port $port)
            if [ -n "$pid" ]; then
                log "杀死占用端口 $port 的进程 (PID: $pid)"
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    sleep 2
    
    # 启动所有服务
    start_backend
    start_frontend
    start_streamlit
}

# 主程序
main() {
    log "=========================================="
    log "OpenManus 服务监控系统启动"
    log "=========================================="
    
    # 初始化和启动
    init_and_start
    
    # 开始监控
    monitor_services
}

# 捕获退出信号
trap 'log "监控系统已停止"; exit 0' SIGTERM SIGINT

# 启动
main
