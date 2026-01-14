#!/usr/bin/env python3
"""
DatabaseTool 测试套件
测试 MySQL 数据库工具的各项功能
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

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
    logger.info("🚀 DatabaseTool 测试开始")
    logger.info("=" * 80)

    db = DatabaseTool()
    test_table = "test_opportunities"
    results = []

    # 测试1: 数据库连接
    logger.info("\n【测试1】数据库连接")
    try:
        result = await db.execute(
            action="execute",
            sql="SELECT 1 as connection_test"
        )
        if result.output:
            logger.info(f"✅ 通过: 数据库连接成功")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试2: 创建表
    logger.info("\n【测试2】创建表")
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
        if result.output:
            logger.info(f"✅ 通过: 表创建成功 ({test_table})")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试3: 插入数据
    logger.info("\n【测试3】插入数据")
    try:
        data = {
            "platform": "upwork",
            "platform_id": "test_001",
            "title": "Build Python AI Agent",
            "description": "We need an AI agent for automation",
            "budget_min": 50.00,
            "budget_max": 100.00,
            "skills_required": json.dumps(["Python", "AI", "LLM"]),
            "status": 1
        }
        result = await db.execute(
            action="upsert",
            table=test_table,
            data=data
        )
        if result.output:
            logger.info(f"✅ 通过: 数据插入成功 ({result.output} 条记录)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试4: 查询数据
    logger.info("\n【测试4】查询数据")
    try:
        result = await db.execute(
            action="query",
            table=test_table,
            limit=10
        )
        if result.output:
            records = result.output if isinstance(result.output, list) else []
            logger.info(f"✅ 通过: 查询成功 ({len(records)} 条记录)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试5: 条件查询
    logger.info("\n【测试5】条件查询")
    try:
        result = await db.execute(
            action="query",
            table=test_table,
            where="platform='upwork'",
            limit=10
        )
        if result.output:
            records = result.output if isinstance(result.output, list) else []
            logger.info(f"✅ 通过: 条件查询成功 ({len(records)} 条记录)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试6: 更新数据
    logger.info("\n【测试6】更新数据")
    try:
        data = {
            "platform": "upwork",
            "platform_id": "test_001",
            "title": "Build Python AI Agent (Updated)",
            "status": 2
        }
        result = await db.execute(
            action="upsert",
            table=test_table,
            data=data
        )
        if result.output:
            logger.info(f"✅ 通过: 数据更新成功 ({result.output} 条记录)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试7: 获取表结构
    logger.info("\n【测试7】获取表结构")
    try:
        result = await db.execute(
            action="get_table_schema",
            table=test_table
        )
        if result.output:
            schema = result.output if isinstance(result.output, list) else []
            logger.info(f"✅ 通过: 获取表结构成功 ({len(schema)} 个字段)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试8: 删除数据
    logger.info("\n【测试8】删除数据")
    try:
        result = await db.execute(
            action="delete",
            table=test_table,
            where="platform_id='test_001'"
        )
        if result.output:
            logger.info(f"✅ 通过: 数据删除成功 ({result.output} 条记录)")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 测试9: 清理表
    logger.info("\n【测试9】清理表")
    try:
        sql = f"DROP TABLE IF EXISTS {test_table}"
        result = await db.execute(action="execute", sql=sql)
        if result.output:
            logger.info(f"✅ 通过: 测试表删除成功")
            results.append(True)
        else:
            logger.info(f"❌ 失败: {result.error}")
            results.append(False)
    except Exception as e:
        logger.info(f"❌ 异常: {str(e)}")
        results.append(False)

    # 输出测试总结
    logger.info("\n" + "=" * 80)
    logger.info("📊 测试总结")
    logger.info("=" * 80)

    passed = sum(1 for r in results if r)
    total = len(results)

    test_names = [
        "数据库连接",
        "创建表",
        "插入数据",
        "查询数据",
        "条件查询",
        "更新数据",
        "获取表结构",
        "删除数据",
        "清理表"
    ]

    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{status}: {name}")

    logger.info("-" * 80)
    logger.info(f"总计: {passed}/{total} 通过")
    logger.info("=" * 80)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
