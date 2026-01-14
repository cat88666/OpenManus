#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取器基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from app.logger import logger


class BaseScraper(ABC):
    """抓取器基类"""

    def __init__(self):
        self.platform_name = "unknown"

    @abstractmethod
    async def scrape_jobs(
        self, keywords: List[str], filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        抓取职位信息

        Args:
            keywords: 搜索关键词列表
            filters: 过滤条件

        Returns:
            职位列表
        """
        pass

    def _normalize_job(self, raw_job: Dict) -> Dict:
        """
        标准化职位数据格式

        Args:
            raw_job: 原始职位数据

        Returns:
            标准化后的职位数据
        """
        return {
            "id": raw_job.get("id", ""),
            "platform": self.platform_name,
            "title": raw_job.get("title", ""),
            "description": raw_job.get("description", ""),
            "budget": self._parse_budget(raw_job.get("budget", "")),
            "tech_stack": self._extract_tech_stack(raw_job.get("description", "")),
            "client_info": raw_job.get("client", {}),
            "url": raw_job.get("url", ""),
            "posted_at": raw_job.get("posted_at", datetime.now().isoformat()),
            "scraped_at": datetime.now().isoformat(),
            "raw_data": raw_job,
        }

    def _parse_budget(self, budget_str: str) -> float:
        """
        解析预算字符串

        Args:
            budget_str: 预算字符串,如 "$500", "$500-$1000"

        Returns:
            预算数值
        """
        try:
            # 移除货币符号和逗号
            clean_str = str(budget_str).replace("$", "").replace(",", "").strip()

            # 处理范围 "$500-$1000"
            if "-" in clean_str:
                parts = clean_str.split("-")
                return float(parts[0].strip())

            # 处理 "Hourly: $50-$100"
            if ":" in clean_str:
                clean_str = clean_str.split(":")[1].strip()
                if "-" in clean_str:
                    return float(clean_str.split("-")[0].strip())

            return float(clean_str) if clean_str else 0.0
        except Exception as e:
            logger.warning(f"预算解析失败: {budget_str}, 错误: {e}")
            return 0.0

    def _extract_tech_stack(self, description: str) -> List[str]:
        """
        从描述中提取技术栈

        Args:
            description: 职位描述

        Returns:
            技术栈列表
        """
        common_techs = [
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Python",
            "Django",
            "FastAPI",
            "JavaScript",
            "TypeScript",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "MySQL",
            "Redis",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "REST API",
            "GraphQL",
            "Next.js",
            "Express",
            "Flask",
            "Spring Boot",
            "Java",
            "Go",
            "Rust",
            "Machine Learning",
            "AI",
            "Data Science",
        ]

        found_techs = []
        description_lower = description.lower()

        for tech in common_techs:
            if tech.lower() in description_lower:
                found_techs.append(tech)

        return found_techs
