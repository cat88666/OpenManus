#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 推送服务

负责将工作信息推送到 Telegram。
"""

from typing import List

import httpx

# 处理直接运行时的路径问题
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 添加项目根目录到 Python 路径
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.jobs.models import Job, TelegramConfig
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
        payload = {
            "chat_id": self.config.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    logger.info("Telegram 消息发送成功")
                    return True
                else:
                    logger.error(
                        f"Telegram 消息发送失败: {response.status_code} - {response.text}"
                    )
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
            # 转义标题中的 Markdown 特殊字符（但保留外层的 * 用于加粗）
            title_escaped = (
                job.title.replace("*", "\\*")
                .replace("_", "\\_")
                .replace("[", "\\[")
                .replace("]", "\\]")
            )
            message += f"📍 *{title_escaped}*\n"
            # 转义公司名称中的特殊字符
            company_escaped = job.company.replace("_", "\\_").replace("*", "\\*")
            message += f"🏢 公司: {company_escaped}\n"
            # 转义地区中的特殊字符
            location_escaped = job.location.replace("_", "\\_").replace("*", "\\*")
            message += f"🌍 地区: {location_escaped}\n"
            if job.published_date:
                message += f"📅 发布时间: {job.published_date}\n"
            if job.salary_range:
                # 转义薪资中的特殊字符（$ 在 Markdown 中可能需要转义）
                salary_escaped = (
                    job.salary_range.replace("$", "\\$")
                    .replace("_", "\\_")
                    .replace("*", "\\*")
                )
                message += f"💰 薪资: {salary_escaped}\n"
            message += f"🔗 [查看详情]({job.url})\n"
            source_escaped = job.source.replace("_", "\\_").replace("*", "\\*")
            message += f"📦 来源: {source_escaped}\n\n"

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


if __name__ == "__main__":
    """
    测试入口：可以直接运行此文件进行测试
    """
    from app.jobs.config_loader import ConfigLoader
    from app.logger import define_log_level, logger
    import asyncio

    async def test():
        """测试 Telegram 服务"""
        define_log_level(name="job_scanner")
        logger.info("测试 Telegram 服务...")

        try:
            config = ConfigLoader.load_config()
            service = TelegramService(config.telegram)

            # 创建测试工作
            test_job = Job(
                id="test_1",
                title="Test Senior Java Developer (Backend)",
                company="Test & Company",
                location="Remote (US)",
                url="https://example.com",
                source="Test",
                published_date="2026-01-13",
                salary_range="$100k-150k",
            )

            # 测试消息格式化
            message = service.format_jobs_message([test_job])
            logger.info("消息格式测试:")
            print("\n" + "=" * 50)
            print(message)
            print("=" * 50 + "\n")

            # 询问是否发送测试消息
            send = input("是否发送测试消息到 Telegram? (y/n): ").strip().lower()
            if send == "y":
                success = await service.send_jobs([test_job])
                if success:
                    logger.info("✅ 测试消息发送成功！")
                else:
                    logger.error("❌ 测试消息发送失败！")
            else:
                logger.info("跳过发送测试消息")

        except Exception as e:
            logger.error(f"测试失败: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(test())
