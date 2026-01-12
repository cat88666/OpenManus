"""
异步任务模块 - Celery任务定义
"""
import logging
from celery import Celery
from config import settings
from database import SessionLocal
from oracle_service import OracleService, KnowledgeBaseService, DeliveryService

logger = logging.getLogger(__name__)

# 创建Celery应用
celery_app = Celery(
    "ai_labor_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


# ==================== 抓取任务 ====================

@celery_app.task(name="scrape_opportunities")
def scrape_opportunities_task(user_id: str, platforms: list = None):
    """
    抓取机会任务
    
    Args:
        user_id: 用户ID
        platforms: 平台列表
    """
    db = SessionLocal()
    try:
        oracle_service = OracleService(db)
        
        logger.info(f"开始为用户{user_id}抓取机会...")
        
        # 这是一个同步函数，但在实际应用中应该使用async
        # 这里简化处理
        
        logger.info(f"用户{user_id}的机会抓取完成")
        
        return {"status": "success", "user_id": user_id}
    
    except Exception as e:
        logger.error(f"抓取机会失败: {e}")
        return {"status": "failed", "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="analyze_opportunities")
def analyze_opportunities_task(user_id: str, limit: int = 10):
    """
    分析机会任务
    
    Args:
        user_id: 用户ID
        limit: 分析数量限制
    """
    db = SessionLocal()
    try:
        oracle_service = OracleService(db)
        
        logger.info(f"开始为用户{user_id}分析机会...")
        
        logger.info(f"用户{user_id}的机会分析完成")
        
        return {"status": "success", "user_id": user_id}
    
    except Exception as e:
        logger.error(f"分析机会失败: {e}")
        return {"status": "failed", "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="daily_scrape_and_analyze")
def daily_scrape_and_analyze_task():
    """
    每日抓取和分析任务
    """
    db = SessionLocal()
    try:
        from crud import UserCRUD
        
        logger.info("开始每日抓取和分析...")
        
        # 获取所有活跃用户
        users = db.query(db.model.User).filter(db.model.User.is_active == 1).all()
        
        for user in users:
            # 抓取机会
            scrape_opportunities_task.delay(user.id)
            
            # 分析机会
            analyze_opportunities_task.delay(user.id)
        
        logger.info(f"每日任务完成，处理了{len(users)}个用户")
        
        return {"status": "success", "users_processed": len(users)}
    
    except Exception as e:
        logger.error(f"每日任务失败: {e}")
        return {"status": "failed", "error": str(e)}
    
    finally:
        db.close()


# ==================== 通知任务 ====================

@celery_app.task(name="send_opportunity_notification")
def send_opportunity_notification_task(user_id: str, opportunity_id: str):
    """
    发送机会通知任务
    
    Args:
        user_id: 用户ID
        opportunity_id: 机会ID
    """
    try:
        from crud import UserCRUD, OpportunityCRUD
        
        db = SessionLocal()
        
        user = UserCRUD.get_by_id(db, user_id)
        opportunity = OpportunityCRUD.get_by_id(db, opportunity_id)
        
        if not user or not opportunity:
            return {"status": "failed", "error": "User or opportunity not found"}
        
        logger.info(f"发送通知给用户{user.email}: {opportunity.title}")
        
        # 这里应该实现实际的邮件或Telegram发送
        # send_email(user.email, f"新机会: {opportunity.title}")
        
        db.close()
        
        return {"status": "success", "user_id": user_id, "opportunity_id": opportunity_id}
    
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="send_daily_report")
def send_daily_report_task(user_id: str):
    """
    发送每日报告任务
    
    Args:
        user_id: 用户ID
    """
    try:
        from crud import UserCRUD
        from oracle_service import OracleService
        
        db = SessionLocal()
        
        user = UserCRUD.get_by_id(db, user_id)
        
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        oracle_service = OracleService(db)
        
        # 获取统计数据
        stats = oracle_service.get_application_stats(user_id)
        
        logger.info(f"为用户{user.email}生成每日报告")
        
        # 这里应该实现实际的邮件发送
        # send_email(user.email, generate_report_html(stats))
        
        db.close()
        
        return {"status": "success", "user_id": user_id, "stats": stats}
    
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return {"status": "failed", "error": str(e)}


# ==================== 项目任务 ====================

@celery_app.task(name="generate_project_report")
def generate_project_report_task(project_id: str):
    """
    生成项目报告任务
    
    Args:
        project_id: 项目ID
    """
    try:
        from crud import ProjectCRUD
        from oracle_service import DeliveryService
        
        db = SessionLocal()
        
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {"status": "failed", "error": "Project not found"}
        
        delivery_service = DeliveryService(db)
        
        # 获取项目进度
        progress = delivery_service.get_project_progress(project_id)
        
        logger.info(f"为项目{project.title}生成报告")
        
        db.close()
        
        return {"status": "success", "project_id": project_id, "progress": progress}
    
    except Exception as e:
        logger.error(f"生成项目报告失败: {e}")
        return {"status": "failed", "error": str(e)}


# ==================== 知识库任务 ====================

@celery_app.task(name="update_knowledge_base")
def update_knowledge_base_task(project_id: str):
    """
    更新知识库任务
    
    Args:
        project_id: 项目ID
    """
    try:
        from crud import ProjectCRUD
        
        db = SessionLocal()
        
        project = ProjectCRUD.get_by_id(db, project_id)
        
        if not project:
            return {"status": "failed", "error": "Project not found"}
        
        knowledge_service = KnowledgeBaseService(db)
        
        logger.info(f"更新项目{project.title}的知识库")
        
        # 这里应该实现实际的知识库更新逻辑
        # 例如：扫描项目文件，提取代码片段，生成embedding等
        
        db.close()
        
        return {"status": "success", "project_id": project_id}
    
    except Exception as e:
        logger.error(f"更新知识库失败: {e}")
        return {"status": "failed", "error": str(e)}


# ==================== 定时任务 ====================

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # 每天早上8点抓取和分析机会
    "daily-scrape-analyze": {
        "task": "daily_scrape_and_analyze",
        "schedule": crontab(hour=8, minute=0),
    },
    # 每天下午5点发送每日报告
    "daily-report": {
        "task": "send_daily_report",
        "schedule": crontab(hour=17, minute=0),
    },
}


# ==================== 任务监控 ====================

@celery_app.task(name="monitor_tasks")
def monitor_tasks():
    """
    监控任务健康状态
    """
    try:
        logger.info("监控任务执行中...")
        
        # 这里可以添加任务监控逻辑
        # 例如：检查失败的任务、统计执行时间等
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"任务监控失败: {e}")
        return {"status": "failed", "error": str(e)}
