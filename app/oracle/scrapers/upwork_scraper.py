#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upwork抓取器 - 基于Playwright
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .base_scraper import BaseScraper
from app.logger import logger


class UpworkScraper(BaseScraper):
    """Upwork抓取器 - 基于Playwright"""

    def __init__(self):
        super().__init__()
        self.platform_name = "upwork"
        self.base_url = "https://www.upwork.com"
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        """初始化浏览器"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # 设为False可以看到浏览器操作
                args=["--disable-blink-features=AutomationControlled"],
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            self.page = await self.context.new_page()
            logger.info("浏览器初始化完成")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise

    async def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"浏览器关闭失败: {e}")

    async def scrape_jobs(
        self, keywords: List[str], filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        抓取Upwork职位

        Args:
            keywords: 搜索关键词列表
            filters: 过滤条件,如 {'min_budget': 500, 'job_type': 'fixed'}

        Returns:
            职位列表
        """
        all_jobs = []

        try:
            if not self.page:
                await self.initialize()

            for keyword in keywords:
                logger.info(f"开始抓取关键词: {keyword}")
                jobs = await self._scrape_by_keyword(keyword, filters)
                all_jobs.extend(jobs)
                logger.info(f"关键词 '{keyword}' 抓取到 {len(jobs)} 个职位")

                # 避免请求过快
                await asyncio.sleep(2)

            # 去重
            unique_jobs = self._deduplicate_jobs(all_jobs)
            logger.info(f"去重后共 {len(unique_jobs)} 个职位")

            return unique_jobs

        except Exception as e:
            logger.error(f"抓取失败: {e}")
            return all_jobs

    async def _scrape_by_keyword(
        self, keyword: str, filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        根据关键词抓取

        Args:
            keyword: 搜索关键词
            filters: 过滤条件

        Returns:
            职位列表
        """
        jobs = []

        try:
            # 构建搜索URL
            search_url = (
                f"{self.base_url}/nx/search/jobs/?q={keyword.replace(' ', '+')}"
            )

            # 添加过滤条件
            if filters:
                if "min_budget" in filters:
                    search_url += f"&amount={filters['min_budget']}-"
                if "job_type" in filters:  # fixed, hourly
                    search_url += f"&t={filters['job_type']}"

            logger.info(f"访问URL: {search_url}")

            # 访问搜索页面
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)  # 等待页面加载

            # 尝试页面解析
            jobs = await self._parse_page()

            return jobs

        except Exception as e:
            logger.error(f"抓取关键词 '{keyword}' 失败: {e}")
            return []

    async def _parse_page(self) -> List[Dict]:
        """
        解析页面HTML获取职位

        Returns:
            职位列表
        """
        jobs = []

        try:
            # 等待职位卡片加载 - 尝试多个可能的选择器
            selectors = [
                '[data-test="job-tile"]',
                'article[data-test="JobTile"]',
                ".job-tile",
                "section.air3-card",
            ]

            job_cards = None
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    job_cards = await self.page.query_selector_all(selector)
                    if job_cards:
                        logger.info(
                            f"使用选择器 '{selector}' 找到 {len(job_cards)} 个职位卡片"
                        )
                        break
                except:
                    continue

            if not job_cards:
                logger.warning("未找到职位卡片")
                return []

            # 解析每个职位卡片
            for card in job_cards[:20]:  # 限制前20个
                try:
                    job_data = await self._extract_job_from_card(card)
                    if job_data and job_data.get("title"):
                        jobs.append(self._normalize_job(job_data))
                except Exception as e:
                    logger.error(f"解析职位卡片失败: {e}")
                    continue

            return jobs

        except Exception as e:
            logger.error(f"页面解析失败: {e}")
            return []

    async def _extract_job_from_card(self, card) -> Dict:
        """
        从职位卡片提取信息

        Args:
            card: 职位卡片元素

        Returns:
            职位数据字典
        """
        try:
            job_data = {}

            # 提取标题和链接
            title_selectors = [
                '[data-test="job-title-link"]',
                "h2 a",
                ".job-title a",
                'a[href*="/jobs/"]',
            ]

            for selector in title_selectors:
                title_elem = await card.query_selector(selector)
                if title_elem:
                    job_data["title"] = (await title_elem.inner_text()).strip()
                    job_data["url"] = await title_elem.get_attribute("href")
                    break

            # 提取描述
            desc_selectors = [
                '[data-test="job-description-text"]',
                ".job-description",
                'p[data-test="UpCLineClamp"]',
            ]

            for selector in desc_selectors:
                desc_elem = await card.query_selector(selector)
                if desc_elem:
                    job_data["description"] = (await desc_elem.inner_text()).strip()
                    break

            # 提取预算
            budget_selectors = [
                '[data-test="job-type-label"]',
                '[data-test="is-fixed-price"]',
                'strong[data-test*="budget"]',
                'li:has-text("$")',
            ]

            for selector in budget_selectors:
                budget_elem = await card.query_selector(selector)
                if budget_elem:
                    job_data["budget"] = (await budget_elem.inner_text()).strip()
                    break

            # 提取发布时间
            time_elem = await card.query_selector(
                '[data-test*="date"], time, span:has-text("ago")'
            )
            if time_elem:
                job_data["posted_at"] = (await time_elem.inner_text()).strip()

            # 提取客户信息
            job_data["client"] = {}

            # 提取ID (从URL)
            if job_data.get("url"):
                url = job_data["url"]
                if "~" in url:
                    job_data["id"] = url.split("~")[-1].split("?")[0]
                else:
                    job_data["id"] = url.split("/")[-1].split("?")[0]

                # 确保URL完整
                if not url.startswith("http"):
                    job_data["url"] = f"{self.base_url}{url}"

            return job_data

        except Exception as e:
            logger.error(f"提取卡片信息失败: {e}")
            return {}

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        去重职位列表

        Args:
            jobs: 职位列表

        Returns:
            去重后的职位列表
        """
        seen_ids = set()
        unique_jobs = []

        for job in jobs:
            job_id = job.get("id")
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)

        return unique_jobs
