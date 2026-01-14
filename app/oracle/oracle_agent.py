#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle智能体 - 机会感知引擎的核心控制器
"""

from typing import List, Dict, Optional
from datetime import datetime
from .scrapers.upwork_scraper import UpworkScraper
from .analyzer.smart_filter import OpportunityAnalyzer
from .storage.opportunity_db import OpportunityDB
from app.logger import logger


class OracleAgent:
    """Oracle智能体 - 整合抓取、分析、存储的完整流程"""

    def __init__(
        self,
        my_skills: Optional[List[str]] = None,
        min_budget: float = 300
    ):
        """
        初始化Oracle智能体

        Args:
            my_skills: 我的技能列表
            min_budget: 最低预算要求
        """
        self.scraper = UpworkScraper()
        self.analyzer = OpportunityAnalyzer(my_skills=my_skills, min_budget=min_budget)
        self.db = OpportunityDB()  # 使用MySQL openmanus库
        logger.info("Oracle智能体初始化完成")

    async def discover_opportunities(
        self,
        keywords: List[str],
        filters: Optional[Dict] = None,
        auto_save: bool = True
    ) -> List[Dict]:
        """
        发现机会 - 完整流程

        Args:
            keywords: 搜索关键词列表
            filters: 过滤条件
            auto_save: 是否自动保存到数据库

        Returns:
            分析后的机会列表
        """
        logger.info("="*60)
        logger.info("开始机会发现流程")
        logger.info("="*60)

        try:
            # 步骤1: 抓取职位
            logger.info(f"\n[步骤1] 抓取职位 - 关键词: {keywords}")
            raw_jobs = await self.scraper.scrape_jobs(keywords, filters)
            logger.info(f"抓取完成: {len(raw_jobs)} 个职位\n")

            if not raw_jobs:
                logger.warning("未抓取到职位")
                return []

            # 步骤2: LLM分析
            logger.info("[步骤2] AI智能分析")
            analyzed_jobs = await self.analyzer.batch_analyze(raw_jobs)
            logger.info(f"分析完成: {len(analyzed_jobs)} 个职位\n")

            # 步骤3: 保存到数据库
            if auto_save:
                logger.info("[步骤3] 保存到数据库")
                saved_count = self.db.batch_save(analyzed_jobs)
                logger.info(f"保存完成: {saved_count} 条\n")

            return analyzed_jobs

        except Exception as e:
            logger.error(f"机会发现流程失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_daily_report(self, top_n: int = 10, min_score: float = 70) -> Dict:
        """
        获取每日报告

        Args:
            top_n: Top N机会
            min_score: 最低分数

        Returns:
            报告数据
        """
        logger.info("="*60)
        logger.info("每日机会报告")
        logger.info("="*60)

        # 获取Top机会
        top_opportunities = self.db.get_top_opportunities(limit=top_n, min_score=min_score)

        # 获取统计信息
        stats = self.db.get_statistics()

        # 生成报告
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'statistics': stats,
            'top_opportunities': top_opportunities,
            'recommendations': []
        }

        # 添加推荐
        for opp in top_opportunities:
            analysis = opp.get('analysis', {})
            if analysis.get('recommended', False):
                report['recommendations'].append({
                    'id': opp['id'],
                    'title': opp['title'],
                    'score': analysis.get('score', 0),
                    'reason': analysis.get('reason', ''),
                    'suggested_bid': analysis.get('suggested_bid', 0),
                    'url': opp.get('url', '')
                })

        return report

    def print_daily_report(self, top_n: int = 10, min_score: float = 70):
        """
        打印每日报告

        Args:
            top_n: Top N机会
            min_score: 最低分数
        """
        report = self.get_daily_report(top_n, min_score)
        stats = report['statistics']

        print(f"\n📅 日期: {report['date']}")
        print("\n📊 统计信息:")
        print(f"   总机会数: {stats.get('total', 0)}")
        print(f"   新机会: {stats.get('new_count', 0)}")
        print(f"   已申请: {stats.get('applied_count', 0)}")
        print(f"   高分机会(≥80): {stats.get('high_score_count', 0)}")
        print(f"   平均分: {stats.get('avg_score', 0):.1f}")

        print(f"\n🏆 Top {len(report['top_opportunities'])} 机会:")
        for i, opp in enumerate(report['top_opportunities'], 1):
            analysis = opp.get('analysis', {})
            print(f"\n【{i}】[评分: {analysis.get('score', 0)}] {opp['title']}")
            print(f"   💰 预算: ${opp['budget']:.0f}")

            tech_stack = opp.get('tech_stack', [])
            if tech_stack:
                print(f"   🔧 技术: {', '.join(tech_stack[:5])}")

            print(f"   📝 理由: {analysis.get('reason', 'N/A')}")
            print(f"   🔗 链接: {opp.get('url', '')}")

            if analysis.get('recommended'):
                suggested_bid = analysis.get('suggested_bid', 0)
                print(f"   ✅ 推荐申请 | 建议出价: ${suggested_bid:.0f}")

                strengths = analysis.get('strengths', [])
                if strengths:
                    print(f"   💪 优势: {', '.join(strengths[:3])}")

                risks = analysis.get('risks', [])
                if risks:
                    print(f"   ⚠️  风险: {', '.join(risks[:3])}")
            else:
                print(f"   ❌ 不推荐")

    async def cleanup(self):
        """清理资源"""
        try:
            await self.scraper.close()
            self.db.close()
            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")

