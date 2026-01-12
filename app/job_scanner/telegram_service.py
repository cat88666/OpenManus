#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 推送服务

负责将工作信息推送到 Telegram。
"""

from typing import List

import httpx

from app.job_scanner.models import Job, TelegramConfig
from app.logger import logger


class TelegramService:
    """Telegram 推送服务"""

    def __init__(self, config: TelegramConfig):
        """
        初始化 Telegram 服务

        Args:
            config: Telegram 配置
        """
        self.config = config
        self.base_url = f"https://api.telegram.org/bot{config.token}"

    async def send_message(self, text: str) -> bool:
        """
        发送消息到 Telegram

        Args:
            text: 消息内容

        Returns:
            bool: 是否发送成功
        """
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.config.chat_id, "text": text, "parse_mode": "Markdown"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info("Telegram 消息发送成功")
                    return True
                else:
                    logger.error(f"Telegram 消息发送失败: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Telegram 消息发送异常: {e}")
            return False

    def format_jobs_message(self, jobs: List[Job]) -> str:
        """
        格式化工作列表为消息

        Args:
            jobs: 工作列表

        Returns:
            str: 格式化后的消息
        """
        if not jobs:
            return ""

        message = "*🚀 远程 Java 资深岗位推送*\n\n"
        for job in jobs:
            message += f"📍 *{job.title}*\n"
            message += f"🏢 公司: {job.company}\n"
            message += f"🌍 地区: {job.location}\n"
            message += f"🔗 [查看详情]({job.url})\n"
            message += f"📦 来源: {job.source}\n\n"

        return message

    async def send_jobs(self, jobs: List[Job], max_per_message: int = 10) -> bool:
        """
        发送工作列表到 Telegram

        Args:
            jobs: 工作列表
            max_per_message: 每条消息的最大工作数量

        Returns:
            bool: 是否全部发送成功
        """
        if not jobs:
            return True

        # 分批发送
        success = True
        for i in range(0, len(jobs), max_per_message):
            batch = jobs[i : i + max_per_message]
            message = self.format_jobs_message(batch)
            if message:
                result = await self.send_message(message)
                if not result:
                    success = False

        return success

