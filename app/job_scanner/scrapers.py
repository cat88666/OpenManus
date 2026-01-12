#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
各网站爬虫实现

实现不同网站的具体爬取逻辑。
"""

import xml.etree.ElementTree as ET
from typing import List

import httpx

from app.job_scanner.base_scraper import BaseScraper
from app.job_scanner.models import Job, SiteConfig
from app.logger import logger


class RemotiveScraper(BaseScraper):
    """Remotive 网站爬虫"""

    async def fetch_jobs(self) -> List[Job]:
        """获取 Remotive 工作列表"""
        jobs = []
        url = self.config.url
        if self.config.search_query:
            url = f"{url}?search={self.config.search_query}"

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for job_data in data.get("jobs", []):
                        jobs.append(
                            Job(
                                id=f"remotive_{job_data['id']}",
                                title=job_data.get("title", ""),
                                company=job_data.get("company_name", ""),
                                location=job_data.get("candidate_required_location", "Worldwide"),
                                url=job_data.get("url", ""),
                                source=self.name,
                                description=job_data.get("description", ""),
                            )
                        )
            except Exception as e:
                logger.error(f"{self.name}: 请求失败 - {e}")

        return jobs


class WWRScraper(BaseScraper):
    """We Work Remotely 网站爬虫"""

    async def fetch_jobs(self) -> List[Job]:
        """获取 WWR RSS 工作列表"""
        jobs = []

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.get(self.config.url)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    for item in root.findall(".//item"):
                        title_elem = item.find("title")
                        desc_elem = item.find("description")
                        link_elem = item.find("link")

                        if title_elem is not None and link_elem is not None:
                            title = title_elem.text or ""
                            description = desc_elem.text if desc_elem is not None else ""
                            link = link_elem.text or ""

                            jobs.append(
                                Job(
                                    id=f"wwr_{link}",
                                    title=title,
                                    company="WWR",
                                    location="Remote",
                                    url=link,
                                    source=self.name,
                                    description=description,
                                )
                            )
            except Exception as e:
                logger.error(f"{self.name}: 请求失败 - {e}")

        return jobs


class RemoteOKScraper(BaseScraper):
    """Remote OK 网站爬虫"""

    async def fetch_jobs(self) -> List[Job]:
        """获取 Remote OK 工作列表"""
        jobs = []

        headers = self.config.headers or {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=self.config.timeout, headers=headers) as client:
            try:
                response = await client.get(self.config.url)
                if response.status_code == 200:
                    data = response.json()
                    # 第一个元素通常是元信息，跳过
                    job_list = data[1:] if isinstance(data, list) else []
                    for job_data in job_list:
                        if not isinstance(job_data, dict):
                            continue

                        jobs.append(
                            Job(
                                id=f"remoteok_{job_data.get('id', '')}",
                                title=job_data.get("position", ""),
                                company=job_data.get("company", ""),
                                location=job_data.get("location", "Remote"),
                                url=f"https://remoteok.com/remote-jobs/{job_data.get('id', '')}",
                                source=self.name,
                                description=job_data.get("description", ""),
                            )
                        )
            except Exception as e:
                logger.error(f"{self.name}: 请求失败 - {e}")

        return jobs


class ArbeitnowScraper(BaseScraper):
    """Arbeitnow 网站爬虫"""

    async def fetch_jobs(self) -> List[Job]:
        """获取 Arbeitnow 工作列表"""
        jobs = []

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.get(self.config.url)
                if response.status_code == 200:
                    data = response.json()
                    job_list = data.get("data", [])
                    for job_data in job_list:
                        jobs.append(
                            Job(
                                id=f"arbeitnow_{job_data.get('slug', '')}",
                                title=job_data.get("title", ""),
                                company=job_data.get("company_name", ""),
                                location=job_data.get("location", "Remote"),
                                url=job_data.get("url", ""),
                                source=self.name,
                                description=job_data.get("description", ""),
                            )
                        )
            except Exception as e:
                logger.error(f"{self.name}: 请求失败 - {e}")

        return jobs


def create_scraper(config: SiteConfig) -> BaseScraper:
    """
    创建爬虫实例

    Args:
        config: 网站配置

    Returns:
        BaseScraper: 爬虫实例

    Raises:
        ValueError: 如果网站类型不支持
    """
    scraper_map = {
        "remotive": RemotiveScraper,
        "wwr": WWRScraper,
        "remoteok": RemoteOKScraper,
        "arbeitnow": ArbeitnowScraper,
    }

    scraper_class = scraper_map.get(config.type.lower())
    if scraper_class is None:
        raise ValueError(f"不支持的网站类型: {config.type}")

    return scraper_class(config)

