#!/usr/bin/env python3
"""
服务健康检查脚本
定期检查所有服务的健康状态，并生成报告
"""

import requests
import json
import time
from datetime import datetime
import subprocess
import os
import sys

# 配置
SERVICES = {
    "后端API": {
        "url": "http://localhost:8000/health",
        "port": 8000,
        "timeout": 5
    },
    "前端应用": {
        "url": "http://localhost:3000",
        "port": 3000,
        "timeout": 5
    },
    "Streamlit仪表板": {
        "url": "http://localhost:8501",
        "port": 8501,
        "timeout": 5
    }
}

LOG_DIR = "/tmp/openmanus_health"
HEALTH_LOG = os.path.join(LOG_DIR, "health_check.log")
CHECK_INTERVAL = 60  # 检查间隔（秒）

# 创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(HEALTH_LOG, "a") as f:
        f.write(log_message + "\n")

def check_port(port):
    """检查端口是否被监听"""
    try:
        result = subprocess.run(
            f"lsof -i :{port} > /dev/null 2>&1",
            shell=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        log(f"❌ 检查端口 {port} 失败: {str(e)}")
        return False

def check_service_health(service_name, service_config):
    """检查单个服务的健康状态"""
    try:
        response = requests.get(
            service_config["url"],
            timeout=service_config["timeout"]
        )
        
        if response.status_code == 200:
            log(f"✅ {service_name} 正常 (HTTP {response.status_code})")
            return True
        else:
            log(f"⚠️ {service_name} 异常 (HTTP {response.status_code})")
            return False
            
    except requests.exceptions.Timeout:
        log(f"❌ {service_name} 超时")
        return False
    except requests.exceptions.ConnectionError:
        log(f"❌ {service_name} 无法连接")
        return False
    except Exception as e:
        log(f"❌ {service_name} 检查失败: {str(e)}")
        return False

def get_service_info(service_name, service_config):
    """获取服务详细信息"""
    info = {
        "name": service_name,
        "port": service_config["port"],
        "url": service_config["url"],
        "timestamp": datetime.now().isoformat(),
        "port_listening": check_port(service_config["port"]),
        "health": check_service_health(service_name, service_config)
    }
    return info

def generate_report(services_info):
    """生成健康检查报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "services": services_info,
        "summary": {
            "total": len(services_info),
            "healthy": sum(1 for s in services_info if s["health"]),
            "unhealthy": sum(1 for s in services_info if not s["health"])
        }
    }
    
    # 保存报告
    report_file = os.path.join(LOG_DIR, "latest_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def print_report(report):
    """打印报告"""
    print("\n" + "="*50)
    print("📊 服务健康检查报告")
    print("="*50)
    print(f"检查时间: {report['timestamp']}")
    print(f"总服务数: {report['summary']['total']}")
    print(f"正常服务: {report['summary']['healthy']}")
    print(f"异常服务: {report['summary']['unhealthy']}")
    print("="*50)
    
    for service in report['services']:
        status = "✅" if service['health'] else "❌"
        port_status = "✅" if service['port_listening'] else "❌"
        print(f"{status} {service['name']}")
        print(f"   端口: {service['port']} ({port_status})")
        print(f"   URL: {service['url']}")
    
    print("="*50 + "\n")

def monitor_services():
    """持续监控服务"""
    log("="*50)
    log("服务健康检查系统启动")
    log("="*50)
    
    while True:
        try:
            log("开始检查服务...")
            
            # 检查所有服务
            services_info = []
            for service_name, service_config in SERVICES.items():
                info = get_service_info(service_name, service_config)
                services_info.append(info)
            
            # 生成报告
            report = generate_report(services_info)
            print_report(report)
            
            # 如果有服务异常，发出警告
            if report['summary']['unhealthy'] > 0:
                log(f"⚠️ 警告: 有 {report['summary']['unhealthy']} 个服务异常")
            
            log(f"下次检查时间: {CHECK_INTERVAL} 秒后")
            log("-"*50)
            
        except Exception as e:
            log(f"❌ 检查过程中出错: {str(e)}")
        
        # 等待下次检查
        time.sleep(CHECK_INTERVAL)

def single_check():
    """执行单次检查"""
    log("执行单次健康检查...")
    
    services_info = []
    for service_name, service_config in SERVICES.items():
        info = get_service_info(service_name, service_config)
        services_info.append(info)
    
    report = generate_report(services_info)
    print_report(report)
    
    # 返回状态码
    return 0 if report['summary']['unhealthy'] == 0 else 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 单次检查模式
        sys.exit(single_check())
    else:
        # 持续监控模式
        try:
            monitor_services()
        except KeyboardInterrupt:
            log("健康检查系统已停止")
            sys.exit(0)
