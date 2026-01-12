#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作扫描器

协调各个爬虫，执行扫描任务并推送新工作。
"""

from typing import List

from app.job_scanner.config_loader import ConfigLoader
from app.job_scanner.models import Job, JobConfig
from app.job_scanner.scrapers import create_scraper
from app.job_scanner.storage import JobStorage
from app.job_scanner.telegram_service import TelegramService
from app.logger import logger


class JobScanner:
    """工作扫描器"""

    def __init__(self, config: JobConfig):
        """
        初始化扫描器

        Args:
            config: 配置对象
        """
        self.config = config
        self.telegram_service = TelegramService(config.telegram)
        self.storage = JobStorage(config.scanner.sent_jobs_file)
        self.scrapers = [
            create_scraper(site_config)
            for site_config in config.scanner.sites
            if site_config.enabled
        ]

    async def scan(self) -> int:
        """
        执行一次扫描

        Returns:
            int: 发现的新工作数量
        """
        logger.info("开始扫描工作...")

        all_jobs: List[Job] = []

        # 并行爬取所有网站
        import asyncio

        tasks = [
            scraper.scrape(
                self.config.scanner.filters.required_keywords,
                self.config.scanner.filters.level_keywords,
            )
            for scraper in self.scrapers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 收集所有工作
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"爬取任务异常: {result}")
                continue
            if isinstance(result, list):
                all_jobs.extend(result)

        # 过滤已发送的工作
        new_jobs = self.storage.get_new_jobs(all_jobs)

        if not new_jobs:
            logger.info("没有发现新工作")
            return 0

        logger.info(f"发现 {len(new_jobs)} 个新工作")

        # 发送到 Telegram
        success = await self.telegram_service.send_jobs(
            new_jobs, self.config.scanner.max_jobs_per_message
        )

        if success:
            # 标记为已发送
            job_ids = {job.id for job in new_jobs}
            self.storage.mark_sent_batch(job_ids)
            logger.info(f"成功推送 {len(new_jobs)} 个新工作")
        else:
            logger.warning("部分工作推送失败，未标记为已发送")

        return len(new_jobs)

