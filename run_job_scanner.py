#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程工作扫描器主程序

定时扫描多个网站的远程工作并推送到 Telegram。
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.job_scanner.scheduler import JobScannerScheduler
from app.logger import define_log_level, logger


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="远程工作扫描器")
    parser.add_argument(
        "--once",
        action="store_true",
        help="只执行一次扫描，不启动定时任务",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="配置文件路径（可选，默认使用 config/job_scanner.toml）",
    )
    return parser.parse_args()


async def main():
    """主函数"""
    args = parse_args()

    # 初始化日志
    define_log_level(name="job_scanner")

    logger.info("=" * 50)
    logger.info("远程工作扫描器启动")
    logger.info("=" * 50)

    try:
        # 创建调度器
        if args.config:
            from app.job_scanner.config_loader import ConfigLoader

            config = ConfigLoader.load_config(args.config)
            scheduler = JobScannerScheduler(config)
        else:
            scheduler = JobScannerScheduler()

        if args.once:
            # 只执行一次
            logger.info("执行单次扫描...")
            count = await scheduler.run_once()
            logger.info(f"扫描完成，发现 {count} 个新工作")
        else:
            # 启动定时任务
            await scheduler.start()

            # 保持运行，等待中断信号
            try:
                while scheduler._running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n收到中断信号，正在关闭...")
                await scheduler.stop()

    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序异常: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    logger.info("程序退出")


if __name__ == "__main__":
    asyncio.run(main())

