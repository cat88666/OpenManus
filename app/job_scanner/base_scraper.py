#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础爬虫抽象类

定义所有网站爬虫的统一接口。
"""

from abc import ABC, abstractmethod
from typing import List

from app.job_scanner.models import Job, SiteConfig
from app.logger import logger


class BaseScraper(ABC):
    """基础爬虫抽象类"""

    def __init__(self, config: SiteConfig):
        """
        初始化爬虫

        Args:
            config: 网站配置
        """
        self.config = config
        self.name = config.name

    @abstractmethod
    async def fetch_jobs(self) -> List[Job]:
        """
        获取工作列表

        Returns:
            List[Job]: 工作列表
        """
        pass

    def _matches_filters(
        self,
        title: str,
        description: str,
        required_keywords: List[str],
        level_keywords: List[str],
    ) -> bool:
        """
        检查工作是否匹配过滤条件

        Args:
            title: 工作标题
            description: 工作描述
            required_keywords: 必须包含的关键词
            level_keywords: 级别关键词

        Returns:
            bool: 是否匹配
        """
        title_lower = title.lower()
        desc_lower = (description or "").lower()

        # 检查必须包含的关键词
        has_required = any(
            keyword.lower() in title_lower or keyword.lower() in desc_lower
            for keyword in required_keywords
        )
        if not has_required:
            return False

        # 检查级别关键词
        has_level = any(keyword.lower() in title_lower for keyword in level_keywords)
        if not has_level:
            return False

        return True

    async def scrape(
        self, required_keywords: List[str], level_keywords: List[str]
    ) -> List[Job]:
        """
        执行爬取并过滤

        Args:
            required_keywords: 必须包含的关键词
            level_keywords: 级别关键词

        Returns:
            List[Job]: 过滤后的工作列表
        """
        try:
            jobs = await self.fetch_jobs()
            filtered_jobs = [
                job
                for job in jobs
                if self._matches_filters(
                    job.title, job.description or "", required_keywords, level_keywords
                )
            ]
            logger.info(
                f"{self.name}: 获取到 {len(jobs)} 个工作，过滤后 {len(filtered_jobs)} 个"
            )
            return filtered_jobs
        except Exception as e:
            logger.error(f"{self.name}: 爬取失败 - {e}")
            return []
