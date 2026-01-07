#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle启动脚本 - Day 1快速验证

使用方法:
python run_oracle.py

或带参数:
python run_oracle.py --keywords "react,python,fastapi" --min-budget 500
"""

import asyncio
import argparse
from app.oracle import OracleAgent
from app.logger import logger


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Oracle - 机会感知引擎')
    parser.add_argument(
        '--keywords',
        type=str,
        default='react,python api,full stack',
        help='搜索关键词,逗号分隔 (默认: react,python api,full stack)'
    )
    parser.add_argument(
        '--min-budget',
        type=float,
        default=300,
        help='最低预算要求 (默认: 300)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='显示Top N机会 (默认: 10)'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=60,
        help='最低评分 (默认: 60)'
    )

    args = parser.parse_args()

    # 解析关键词
    keywords = [k.strip() for k in args.keywords.split(',')]

    logger.info("="*60)
    logger.info("🔮 Oracle - 机会感知引擎启动")
    logger.info("="*60)
    logger.info(f"搜索关键词: {keywords}")
    logger.info(f"最低预算: ${args.min_budget}")
    logger.info("="*60)

    # 初始化Oracle智能体
    oracle = OracleAgent(
        my_skills=[
            "React", "Vue.js", "JavaScript", "TypeScript",
            "Python", "FastAPI", "Django", "Flask",
            "Node.js", "Express",
            "SQL", "PostgreSQL", "MongoDB",
            "REST API", "GraphQL",
            "AWS", "Docker", "Kubernetes"
        ],
        min_budget=args.min_budget
    )

    try:
        # 发现机会
        await oracle.discover_opportunities(
            keywords=keywords,
            filters={
                'min_budget': args.min_budget
            },
            auto_save=True
        )

        # 显示每日报告
        oracle.print_daily_report(
            top_n=args.top_n,
            min_score=args.min_score
        )

    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        await oracle.cleanup()
        logger.info("\n✅ 程序执行完成")


if __name__ == "__main__":
    asyncio.run(main())

