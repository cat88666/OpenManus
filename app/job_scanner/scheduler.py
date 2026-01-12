#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器

实现定时扫描功能。
"""

import asyncio
from typing import Optional

from app.job_scanner.config_loader import ConfigLoader
from app.job_scanner.models import JobConfig
from app.job_scanner.scanner import JobScanner
from app.logger import logger


class JobScannerScheduler:
    """工作扫描调度器"""

    def __init__(self, config: Optional[JobConfig] = None):
        """
        初始化调度器

        Args:
            config: 配置对象，如果为 None 则从文件加载
        """
        if config is None:
            config = ConfigLoader.load_config()
        self.config = config
        self.scanner = JobScanner(config)
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行")
            return

        self._running = True
        logger.info(f"启动工作扫描调度器，扫描间隔: {self.config.scanner.scan_interval} 秒")

        # 立即执行一次扫描
        await self.scanner.scan()

        # 启动定时任务
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """停止调度器"""
        if not self._running:
            return

        logger.info("正在停止调度器...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("调度器已停止")

    async def _run_loop(self) -> None:
        """运行循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.scanner.scan_interval)
                if self._running:
                    await self.scanner.scan()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"扫描循环异常: {e}")
                # 发生异常时等待一段时间再继续
                await asyncio.sleep(10)

    async def run_once(self) -> int:
        """
        执行一次扫描（不启动调度器）

        Returns:
            int: 发现的新工作数量
        """
        return await self.scanner.scan()

