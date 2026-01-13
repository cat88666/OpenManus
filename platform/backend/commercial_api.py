"""
商业化平台完整API接口
支持项目管理、团队管理、财务管理、自动接单等
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import logging

from commercial_finance import FinanceManager, TransactionType, TransactionStatus
from commercial_crawler import RemoteProjectCrawler, AutoSubmissionSystem, AutoAcceptanceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="远程项目承包分包平台 API")

# 全局实例
finance_manager = FinanceManager()
crawler = RemoteProjectCrawler()
submission_system = AutoSubmissionSystem()
acceptance_engine = AutoAcceptanceEngine()


# ==================== Pydantic Models ====================

class TeamMemberCreate(BaseModel):
    """创建团队成员"""
    name: str
    email: str
    skills: List[str]
    hourly_rate: float
    commission_rate: float = 0.25
    usdt_wallet: Optional[str] = None


class TeamMemberUpdate(BaseModel):
    """更新团队成员"""
    name: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[List[str]] = None
    hourly_rate: Optional[float] = None
    commission_rate: Optional[float] = None
    usdt_wallet: Optional[str] = None
    availability: Optional[str] = None


class ProjectCreate(BaseModel):
    """创建项目"""
    title: str
    budget: float
    platform: str
    description: Optional[str] = None
    skills: Optional[List[str]] = None


class ProjectAssign(BaseModel):
    """分配项目"""
    project_id: int
    member_id: int
    estimated_cost: float


class PaymentRequest(BaseModel):
    """支付请求"""
    member_id: int
    amount: float
    usdt_wallet: str
    description: Optional[str] = None


class CrawlerRequest(BaseModel):
    """爬虫请求"""
    platforms: List[str] = ["upwork", "toptal"]
    keywords: List[str] = ["Python", "Django", "React"]


# ==================== 团队管理接口 ====================

@app.post("/api/v1/team/members", tags=["团队管理"])
async def create_team_member(member: TeamMemberCreate):
    """创建团队成员"""
    try:
        new_member = finance_manager.team_manager.add_member(
            name=member.name,
            email=member.email,
            skills=member.skills,
            hourly_rate=member.hourly_rate,
            commission_rate=member.commission_rate,
            usdt_wallet=member.usdt_wallet
        )
        return {
            "success": True,
            "message": f"成员 {member.name} 已创建",
            "member": new_member.to_dict()
        }
    except Exception as e:
        logger.error(f"创建团队成员失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/team/members", tags=["团队管理"])
async def get_all_team_members():
    """获取所有团队成员"""
    try:
        members = finance_manager.team_manager.get_all_members()
        return {
            "success": True,
            "count": len(members),
            "members": [m.to_dict() for m in members]
        }
    except Exception as e:
        logger.error(f"获取团队成员失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/team/members/{member_id}", tags=["团队管理"])
async def get_team_member(member_id: int):
    """获取单个团队成员"""
    try:
        member = finance_manager.team_manager.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")
        return {
            "success": True,
            "member": member.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取团队成员失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/v1/team/members/{member_id}", tags=["团队管理"])
async def update_team_member(member_id: int, member: TeamMemberUpdate):
    """更新团队成员"""
    try:
        existing_member = finance_manager.team_manager.get_member(member_id)
        if not existing_member:
            raise HTTPException(status_code=404, detail="成员不存在")
        
        # 更新字段
        if member.name:
            existing_member.name = member.name
        if member.email:
            existing_member.email = member.email
        if member.skills:
            existing_member.skills = member.skills
        if member.hourly_rate:
            existing_member.hourly_rate = member.hourly_rate
        if member.commission_rate:
            existing_member.commission_rate = member.commission_rate
        if member.usdt_wallet:
            existing_member.usdt_wallet = member.usdt_wallet
        if member.availability:
            existing_member.availability = member.availability
        
        return {
            "success": True,
            "message": f"成员 {existing_member.name} 已更新",
            "member": existing_member.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新团队成员失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/team/performance", tags=["团队管理"])
async def get_team_performance():
    """获取团队绩效"""
    try:
        performance = finance_manager.get_team_performance()
        return {
            "success": True,
            "count": len(performance),
            "performance": performance
        }
    except Exception as e:
        logger.error(f"获取团队绩效失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/team/members/{member_id}/availability", tags=["团队管理"])
async def set_member_availability(member_id: int, availability: str):
    """设置成员可用性"""
    try:
        finance_manager.team_manager.set_member_availability(member_id, availability)
        return {
            "success": True,
            "message": f"成员可用性已设置为: {availability}"
        }
    except Exception as e:
        logger.error(f"设置成员可用性失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 项目管理接口 ====================

@app.post("/api/v1/projects", tags=["项目管理"])
async def create_project(project: ProjectCreate):
    """创建项目"""
    try:
        new_project = finance_manager.create_project(
            title=project.title,
            budget=Decimal(str(project.budget)),
            platform=project.platform
        )
        return {
            "success": True,
            "message": f"项目 {project.title} 已创建",
            "project": new_project.to_dict()
        }
    except Exception as e:
        logger.error(f"创建项目失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/projects", tags=["项目管理"])
async def get_all_projects(status: Optional[str] = None):
    """获取所有项目"""
    try:
        projects = finance_manager.projects.values()
        if status:
            projects = [p for p in projects if p.status == status]
        
        return {
            "success": True,
            "count": len(projects),
            "projects": [p.to_dict() for p in projects]
        }
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/projects/{project_id}", tags=["项目管理"])
async def get_project(project_id: int):
    """获取单个项目"""
    try:
        project = finance_manager.projects.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        return {
            "success": True,
            "project": project.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/projects/assign", tags=["项目管理"])
async def assign_project(assignment: ProjectAssign):
    """分配项目给团队成员"""
    try:
        success = finance_manager.assign_project(
            project_id=assignment.project_id,
            member_id=assignment.member_id,
            estimated_cost=Decimal(str(assignment.estimated_cost))
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="分配失败")
        
        project = finance_manager.projects.get(assignment.project_id)
        return {
            "success": True,
            "message": "项目已分配",
            "project": project.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分配项目失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 财务管理接口 ====================

@app.post("/api/v1/finance/payment", tags=["财务管理"])
async def process_payment(payment: PaymentRequest):
    """处理支付"""
    try:
        success = finance_manager.process_payment(
            member_id=payment.member_id,
            amount=Decimal(str(payment.amount)),
            usdt_wallet=payment.usdt_wallet
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="支付失败")
        
        return {
            "success": True,
            "message": f"支付已处理: ${payment.amount} USDT"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理支付失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/finance/commission/{project_id}", tags=["财务管理"])
async def get_commission(project_id: int):
    """获取项目分成"""
    try:
        commission = finance_manager.calculate_commission(project_id)
        if not commission:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return {
            "success": True,
            "commission": commission
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分成失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/finance/monthly-stats", tags=["财务管理"])
async def get_monthly_stats(year: int = Query(2024), month: int = Query(1)):
    """获取月度统计"""
    try:
        stats = finance_manager.get_monthly_stats(year, month)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"获取月度统计失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 爬虫和自动接单接口 ====================

@app.post("/api/v1/crawler/start", tags=["爬虫系统"])
async def start_crawler(request: CrawlerRequest):
    """启动爬虫"""
    try:
        logger.info(f"启动爬虫: 平台={request.platforms}, 关键词={request.keywords}")
        
        # 这里可以启动异步爬虫任务
        # 实际实现中应该使用Celery或其他任务队列
        
        return {
            "success": True,
            "message": "爬虫已启动",
            "platforms": request.platforms,
            "keywords": request.keywords
        }
    except Exception as e:
        logger.error(f"启动爬虫失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/auto-accept/check", tags=["自动接单"])
async def check_auto_accept(project_id: int):
    """检查项目是否应该自动接单"""
    try:
        project = finance_manager.projects.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        team_members = finance_manager.team_manager.get_all_members()
        
        should_accept = acceptance_engine.should_accept_project(
            project.to_dict(),
            [m.to_dict() for m in team_members]
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "should_accept": should_accept,
            "reason": "项目符合接单条件" if should_accept else "项目不符合接单条件"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查自动接单失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/auto-accept/assign", tags=["自动接单"])
async def auto_assign_project(project_id: int):
    """自动分配项目"""
    try:
        project = finance_manager.projects.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        team_members = finance_manager.team_manager.get_all_members()
        
        assignment = acceptance_engine.assign_project_to_team(
            project.to_dict(),
            [m.to_dict() for m in team_members]
        )
        
        if not assignment:
            raise HTTPException(status_code=400, detail="无法分配项目")
        
        return {
            "success": True,
            "message": "项目已自动分配",
            "assignment": assignment
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"自动分配项目失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 仪表板接口 ====================

@app.get("/api/v1/dashboard/summary", tags=["仪表板"])
async def get_dashboard_summary():
    """获取仪表板摘要"""
    try:
        # 获取当前月份统计
        now = datetime.now()
        stats = finance_manager.get_monthly_stats(now.year, now.month)
        
        # 获取团队信息
        team_members = finance_manager.team_manager.get_all_members()
        available_count = sum(1 for m in team_members if m.availability == "available")
        
        # 获取项目统计
        all_projects = finance_manager.projects.values()
        total_projects = len(all_projects)
        active_projects = sum(1 for p in all_projects if p.status in ["assigned", "in_progress"])
        completed_projects = sum(1 for p in all_projects if p.status == "completed")
        
        return {
            "success": True,
            "summary": {
                "month": f"{now.year}-{now.month:02d}",
                "total_income": stats['total_income'],
                "total_profit": stats['total_profit'],
                "profit_margin": f"{stats['profit_margin']:.2f}%",
                "team_total": len(team_members),
                "team_available": available_count,
                "projects_total": total_projects,
                "projects_active": active_projects,
                "projects_completed": completed_projects
            }
        }
    except Exception as e:
        logger.error(f"获取仪表板摘要失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 健康检查 ====================

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "远程项目承包分包平台"
    }


@app.get("/api/v1/info", tags=["系统"])
async def get_api_info():
    """获取API信息"""
    return {
        "name": "远程项目承包分包平台 API",
        "version": "1.0.0",
        "description": "支持项目管理、团队管理、财务管理、自动接单",
        "endpoints": {
            "team": "/api/v1/team/*",
            "projects": "/api/v1/projects/*",
            "finance": "/api/v1/finance/*",
            "crawler": "/api/v1/crawler/*",
            "auto_accept": "/api/v1/auto-accept/*",
            "dashboard": "/api/v1/dashboard/*"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
