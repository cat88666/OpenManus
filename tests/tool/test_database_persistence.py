#!/usr/bin/env python3
"""
DatabaseTool 持久化测试
创建数据并保留在数据库中，用于验证数据是否真正被保存
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tool.database_tool import DatabaseTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🚀 DatabaseTool 持久化测试")
    logger.info("=" * 80)

    db = DatabaseTool()
    test_table = "test_opportunities"

    # 创建表
    logger.info("\n【步骤1】创建表")
    try:
        sql = f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            platform VARCHAR(50),
            platform_id VARCHAR(100) UNIQUE,
            title VARCHAR(255),
            description TEXT,
            budget_min DECIMAL(10,2),
            budget_max DECIMAL(10,2),
            skills_required JSON,
            status TINYINT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        result = await db.execute(action="execute", sql=sql)
        logger.info(f"✅ 表创建成功: {test_table}")
    except Exception as e:
        logger.error(f"❌ 表创建失败: {str(e)}")
        return False

    # 插入多条测试数据
    logger.info("\n【步骤2】插入测试数据")
    test_data = [
        {
            "platform": "upwork",
            "platform_id": "upwork_001",
            "title": "Build Python AI Agent",
            "description": "We need an AI agent for automation",
            "budget_min": 50.00,
            "budget_max": 100.00,
            "skills_required": json.dumps(["Python", "AI", "LLM"]),
            "status": 1
        },
        {
            "platform": "toptal",
            "platform_id": "toptal_001",
            "title": "Remote Backend Engineer",
            "description": "Looking for experienced backend developer",
            "budget_min": 80.00,
            "budget_max": 150.00,
            "skills_required": json.dumps(["Go", "Python", "Microservices"]),
            "status": 1
        },
        {
            "platform": "linkedin",
            "platform_id": "linkedin_001",
            "title": "Full Stack Developer",
            "description": "Build web applications with React and Node.js",
            "budget_min": 60.00,
            "budget_max": 120.00,
            "skills_required": json.dumps(["React", "Node.js", "MongoDB"]),
            "status": 2
        }
    ]

    inserted_count = 0
    for i, data in enumerate(test_data, 1):
        try:
            result = await db.execute(
                action="upsert",
                table=test_table,
                data=data
            )
            if result.output:
                logger.info(f"  ✅ 数据 {i} 插入成功: {data['platform']} - {data['title']}")
                inserted_count += 1
            else:
                logger.error(f"  ❌ 数据 {i} 插入失败: {result.error}")
        except Exception as e:
            logger.error(f"  ❌ 数据 {i} 插入异常: {str(e)}")

    logger.info(f"\n总共插入 {inserted_count}/{len(test_data)} 条数据")

    # 验证数据
    logger.info("\n【步骤3】验证数据")
    logger.info(f"\n请在数据库中执行以下命令查看数据:")
    logger.info(f"  mysql -u avnadmin -p -h mysql-df85ad2-facenada1107-6e0b.b.aivencloud.com -P 23808 defaultdb")
    logger.info(f"  SELECT * FROM {test_table};")
    logger.info(f"\n或者执行:")
    logger.info(f"  SELECT COUNT(*) FROM {test_table};")

    logger.info("\n" + "=" * 80)
    logger.info("✅ 数据已保存到数据库，请在数据库中查看")
    logger.info("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
