#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块

注意：运行此文件前，请确保已激活 conda 环境：
    conda activate open_manus
"""
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger as _logger

# 尝试导入 PROJECT_ROOT，如果失败（直接运行文件时），则在 __main__ 块中处理
try:
    from app.config import PROJECT_ROOT
except ImportError:
    # 如果直接运行此文件，PROJECT_ROOT 将在 __main__ 块中设置
    PROJECT_ROOT = None


_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None, project_root: Path = None):
    """
    调整日志级别到指定级别以上

    日志文件按日期生成，每天只有一个日志文件。
    格式：logs/YYYYMMDD.log 或 logs/name_YYYYMMDD.log

    Args:
        print_level: 控制台输出日志级别
        logfile_level: 文件日志级别
        name: 日志文件名前缀（可选）
        project_root: 项目根目录路径（如果直接运行文件时需要传入）
    """
    global _print_level
    _print_level = print_level

    # 确定项目根目录
    if project_root is None:
        project_root = PROJECT_ROOT
    if project_root is None:
        # 如果还是 None，使用当前文件的父目录的父目录
        project_root = Path(__file__).resolve().parent.parent

    # 使用日期格式，每天生成一个日志文件
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # 使用日期命名日志文件，每天只有一个文件

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)

    # 使用 rotation 参数实现按天轮转，每天 00:00 自动创建新文件
    # retention 参数设置保留最近 30 天的日志文件
    log_file_path = project_root / f"logs/{log_name}.log"
    _logger.add(
        log_file_path,
        level=logfile_level,
        rotation="00:00",  # 每天 00:00 轮转（创建新文件）
        retention="30 days",  # 保留最近 30 天的日志
        encoding="utf-8",  # 使用 UTF-8 编码
        enqueue=True,  # 线程安全
    )
    return _logger


logger = define_log_level()


if __name__ == "__main__":
    # 当直接运行此文件时，需要将项目根目录添加到 Python 路径
    # 这样才能正确导入 app 模块
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 尝试导入 PROJECT_ROOT（因为路径已添加）
    try:
        from app.config import PROJECT_ROOT
        project_root = PROJECT_ROOT
    except ImportError:
        # 如果还是无法导入，使用计算的路径
        pass

    # 重新初始化 logger（使用正确的路径）
    logger = define_log_level(project_root=project_root)

    # 测试日志功能
    logger.info("应用程序启动")
    logger.debug("调试消息")
    logger.warning("警告消息")
    logger.error("错误消息")
    logger.critical("严重错误消息")

    try:
        raise ValueError("测试错误")
    except Exception as e:
        logger.exception(f"发生错误: {e}")
