# -*- coding: utf-8 -*-
"""
ProjectHunterAgent 测试脚本

用于验证 ProjectHunterAgent 是否能正确执行其工作流：
1. 搜集职位
2. 存入数据库
3. 评估职位

运行方式：
- 在 OpenManus 项目根目录下执行：`python3 test_project_hunter.py`
"""

import asyncio
import os

# 确保在项目根目录下运行，以便正确导入模块
if not os.path.exists("app"):
    print("错误：请在 OpenManus 项目根目录下运行此脚本")
    exit(1)

from app.agent.project_hunter import ProjectHunterAgent
from app.config import config
from app.utils.logger import logger

async def main():
    """
    主函数：创建并运行 ProjectHunterAgent
    """
    logger.info("=" * 80)
    logger.info("🚀 开始测试 ProjectHunterAgent 工作流程")
    logger.info("=" * 80)

    try:
        # 设置数据库密码环境变量（用于测试）
        # 在实际部署中，应通过系统环境变量或.env文件设置
        # 在运行测试前，请确保已设置 DB_PASSWORD 环境变量
        # export DB_PASSWORD="your_actual_password"
        if not os.getenv("DB_PASSWORD"):
            logger.error("错误：请设置 DB_PASSWORD 环境变量后再运行测试")
            return

        # 创建 ProjectHunterAgent 实例
        # 使用 Manus.create() 工厂方法确保所有异步初始化完成
        logger.info("正在创建 ProjectHunterAgent 实例...")
        hunter_agent = await ProjectHunterAgent.create(
            max_steps=10,  # 限制每个子任务的最大步数
        )
        logger.info("✅ ProjectHunterAgent 实例创建成功")

        # 运行完整的工作流程
        logger.info("即将执行 run_workflow 方法...")
        result = await hunter_agent.run_workflow(
            task="搜集最新的AI工程师职位，存入数据库并进行评估"
        )

        # 打印最终结果
        logger.info("=" * 80)
        logger.info("🎉 ProjectHunterAgent 工作流程测试完成")
        logger.info("=" * 80)
        print(result)

    except Exception as e:
        logger.error(f"测试过程中发生严重错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # 设置日志级别
    # config.log_level = "DEBUG"
    # logger.setLevel(config.log_level)
    
    # 运行主函数
    asyncio.run(main())
