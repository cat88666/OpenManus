#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义

使用 Pydantic 定义配置和数据结构。
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TelegramConfig(BaseModel):
    """Telegram 配置"""

    token: str = Field(..., description="Telegram Bot Token")
    chat_id: str = Field(..., description="Telegram Chat ID")


class FilterConfig(BaseModel):
    """过滤配置"""

    required_keywords: List[str] = Field(
        default_factory=lambda: ["java"], description="必须包含的关键词列表"
    )
    level_keywords: List[str] = Field(
        default_factory=lambda: ["senior", "lead", "staff", "principal", "sr.", "10+"],
        description="级别关键词列表",
    )
    exclude_keywords: List[str] = Field(
        default_factory=list, description="排除关键词列表"
    )


class SiteConfig(BaseModel):
    """网站配置"""

    name: str = Field(..., description="网站名称")
    enabled: bool = Field(True, description="是否启用")
    type: str = Field(..., description="网站类型：remotive, wwr, remoteok, arbeitnow")
    url: str = Field(..., description="API 或 RSS 地址")
    timeout: int = Field(15, description="请求超时时间（秒）")
    search_query: Optional[str] = Field(None, description="搜索查询（某些网站需要）")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP 请求头")


class ScannerConfig(BaseModel):
    """扫描器配置"""

    scan_interval: int = Field(60, description="扫描间隔（秒）")
    sent_jobs_file: str = Field(
        "workspace/jobs/sent_jobs.json", description="已发送工作记录文件路径"
    )
    max_jobs_per_message: int = Field(10, description="每次推送的最大工作数量")
    filters: FilterConfig = Field(default_factory=FilterConfig, description="过滤配置")
    sites: List[SiteConfig] = Field(default_factory=list, description="网站配置列表")


class JobConfig(BaseModel):
    """完整配置"""

    telegram: TelegramConfig = Field(..., description="Telegram 配置")
    scanner: ScannerConfig = Field(..., description="扫描器配置")


class Job(BaseModel):
    """工作信息模型"""

    id: str = Field(..., description="工作唯一标识")
    title: str = Field(..., description="工作标题")
    company: str = Field(..., description="公司名称")
    location: str = Field(..., description="工作地点")
    url: str = Field(..., description="工作详情链接")
    source: str = Field(..., description="来源网站")
    description: Optional[str] = Field(None, description="工作描述")
    published_date: Optional[str] = Field(None, description="发布时间")
    salary_range: Optional[str] = Field(None, description="薪资范围")

