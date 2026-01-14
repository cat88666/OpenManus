#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle定时爬虫调度 - 每5秒自动爬取工作机会

使用方法:
python run_oracle_scheduler.py

或带参数:
python run_oracle_scheduler.py --interval 5 --keywords "react,python,go"
"""

import asyncio
import argparse
import signal
from typing import Optional
from app.oracle import OracleAgent
from app.logger import logger


class OracleScheduler:
    """Oracle定时爬虫调度器"""

    def __init__(self, keywords: list, interval: int = 5, min_budget: float = 300):
        """
        初始化调度器

        Args:
            keywords: 搜索关键词列表
            interval: 爬取间隔（秒）
            min_budget: 最低预算
        """
        self.keywords = keywords
        self.interval = interval
        self.min_budget = min_budget
        self.oracle = OracleAgent(
            my_skills=[
                "React", "Vue.js", "JavaScript", "TypeScript",
                "Python", "FastAPI", "Django", "Flask",
                "Node.js", "Express",
                "Java", "Spring Boot", "Kotlin",
                "Go", "Rust",
                "SQL", "PostgreSQL", "MongoDB", "MySQL",
                "REST API", "GraphQL",
                "AWS", "Docker", "Kubernetes",
                "DevOps", "CI/CD"
            ],
            min_budget=min_budget
        )
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行")
            return

        self._running = True
        logger.info("="*60)
        logger.info("🔮 Oracle定时爬虫调度器启动")
        logger.info("="*60)
        logger.info(f"搜索关键词: {self.keywords}")
        logger.info(f"爬取间隔: {self.interval}秒")
        logger.info(f"最低预算: ${self.min_budget}")
        logger.info("="*60)

        # 立即执行一次
        await self._scrape_once()

        # 启动定时任务
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """停止调度器"""
        if not self._running:
            return

        logger.info("\n正在停止调度器...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("调度器已停止")

    async def _scrape_once(self):
        """执行一次爬取"""
        try:
            logger.info(f"\n[{asyncio.get_event_loop().time():.0f}] 开始爬取机会...")
            
            opportunities = await self.oracle.discover_opportunities(
                keywords=self.keywords,
                filters={'min_budget': self.min_budget},
                auto_save=True
            )
            
            if opportunities:
                logger.info(f"✅ 爬取成功: {len(opportunities)} 个机会")
                
                # 显示Top 5
                top_5 = sorted(opportunities, key=lambda x: x.get('ai_score', 0), reverse=True)[:5]
                logger.info("\n📊 Top 5 机会:")
                for i, opp in enumerate(top_5, 1):
                    logger.info(f"  {i}. [{opp.get('platform', 'N/A').upper()}] {opp.get('title', 'N/A')} - ${opp.get('budget', 'N/A')} (评分: {opp.get('ai_score', 0):.1f})")
            else:
                logger.info("⚠️  未找到符合条件的机会")
                
        except Exception as e:
            logger.error(f"❌ 爬取失败: {e}")
            import traceback
            traceback.print_exc()

    async def _run_loop(self):
        """运行循环"""
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                if self._running:
                    await self._scrape_once()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"调度循环异常: {e}")
                await asyncio.sleep(10)


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Oracle定时爬虫调度')
    parser.add_argument(
        '--keywords',
        type=str,
        default='react,python,java,go,frontend,backend',
        help='搜索关键词,逗号分隔'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='爬取间隔（秒）'
    )
    parser.add_argument(
        '--min-budget',
        type=float,
        default=300,
        help='最低预算要求'
    )

    args = parser.parse_args()

    # 解析关键词
    keywords = [k.strip() for k in args.keywords.split(',')]

    # 创建调度器
    scheduler = OracleScheduler(
        keywords=keywords,
        interval=args.interval,
        min_budget=args.min_budget
    )

    # 处理信号
    def signal_handler(sig, frame):
        logger.info("\n收到中断信号，正在关闭...")
        asyncio.create_task(scheduler.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 启动调度器
        await scheduler.start()
        
        # 保持运行
        while scheduler._running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        await scheduler.stop()
        await scheduler.oracle.cleanup()
        logger.info("\n✅ 程序已关闭")


if __name__ == "__main__":
    asyncio.run(main())
