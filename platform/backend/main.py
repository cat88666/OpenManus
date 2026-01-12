"""
FastAPI主应用
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import settings
from database import init_db, get_db
import models
import schemas
import crud
from llm_service import get_llm_service

# 配置日志
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# ==================== 应用启动和关闭事件 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("应用启动中...")
    init_db()
    logger.info("数据库初始化完成")
    yield
    # 关闭
    logger.info("应用关闭中...")


# ==================== 创建FastAPI应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI数字员工平台 - 智能外包接单和交付系统",
    lifespan=lifespan
)

# ==================== CORS配置 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# ==================== 用户API ====================

@app.post("/api/v1/users", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    # 检查用户是否已存在
    existing_user = crud.UserCRUD.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    db_user = crud.UserCRUD.create(db, user)
    return db_user


@app.get("/api/v1/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """获取用户"""
    db_user = crud.UserCRUD.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user


@app.put("/api/v1/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: str,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """更新用户"""
    db_user = crud.UserCRUD.update(db, user_id, user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user


# ==================== 机会API ====================

@app.post("/api/v1/opportunities", response_model=schemas.OpportunityResponse)
async def create_opportunity(
    opportunity: schemas.OpportunityCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """创建机会"""
    db_opportunity = crud.OpportunityCRUD.create(db, opportunity, user_id)
    return db_opportunity


@app.get("/api/v1/opportunities/{opportunity_id}", response_model=schemas.OpportunityResponse)
async def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    """获取机会"""
    db_opportunity = crud.OpportunityCRUD.get_by_id(db, opportunity_id)
    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机会不存在"
        )
    return db_opportunity


@app.get("/api/v1/users/{user_id}/opportunities")
async def list_opportunities(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    platform: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的机会列表"""
    opportunities, total = crud.OpportunityCRUD.list_by_user(
        db, user_id, skip, limit, status, platform
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": opportunities
    }


@app.post("/api/v1/opportunities/{opportunity_id}/analyze")
async def analyze_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
):
    """分析机会"""
    db_opportunity = crud.OpportunityCRUD.get_by_id(db, opportunity_id)
    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机会不存在"
        )
    
    # 调用LLM分析
    llm_service = get_llm_service("openai")
    opportunity_data = {
        "title": db_opportunity.title,
        "description": db_opportunity.description,
        "budget": db_opportunity.budget,
        "tech_stack": db_opportunity.tech_stack or [],
        "client_rating": db_opportunity.client_rating,
        "proposal_count": db_opportunity.proposal_count
    }
    
    analysis = await llm_service.analyze_opportunity(opportunity_data)
    
    # 更新机会
    update_data = schemas.OpportunityUpdate(
        ai_score=analysis.get("score"),
        ai_analysis=analysis
    )
    crud.OpportunityCRUD.update(db, opportunity_id, update_data)
    
    return analysis


@app.get("/api/v1/users/{user_id}/opportunities/top")
async def get_top_opportunities(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取评分最高的机会"""
    opportunities = crud.OpportunityCRUD.get_top_opportunities(db, user_id, limit)
    return {
        "total": len(opportunities),
        "items": opportunities
    }


# ==================== 申请API ====================

@app.post("/api/v1/applications", response_model=schemas.ApplicationResponse)
async def create_application(
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db)
):
    """创建申请"""
    db_application = crud.ApplicationCRUD.create(db, application)
    return db_application


@app.get("/api/v1/applications/{application_id}", response_model=schemas.ApplicationResponse)
async def get_application(application_id: str, db: Session = Depends(get_db)):
    """获取申请"""
    db_application = crud.ApplicationCRUD.get_by_id(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请不存在"
        )
    return db_application


@app.get("/api/v1/opportunities/{opportunity_id}/applications")
async def list_applications(
    opportunity_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取机会的申请列表"""
    applications, total = crud.ApplicationCRUD.list_by_opportunity(
        db, opportunity_id, skip, limit
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": applications
    }


# ==================== 项目API ====================

@app.post("/api/v1/projects", response_model=schemas.ProjectResponse)
async def create_project(
    project: schemas.ProjectCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """创建项目"""
    db_project = crud.ProjectCRUD.create(db, project, user_id)
    return db_project


@app.get("/api/v1/projects/{project_id}", response_model=schemas.ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """获取项目"""
    db_project = crud.ProjectCRUD.get_by_id(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    return db_project


@app.get("/api/v1/users/{user_id}/projects")
async def list_projects(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取用户的项目列表"""
    projects, total = crud.ProjectCRUD.list_by_user(
        db, user_id, skip, limit, status
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": projects
    }


@app.put("/api/v1/projects/{project_id}", response_model=schemas.ProjectResponse)
async def update_project(
    project_id: str,
    project: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目"""
    db_project = crud.ProjectCRUD.update(db, project_id, project)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    return db_project


# ==================== 任务API ====================

@app.post("/api/v1/tasks", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """创建任务"""
    db_task = crud.TaskCRUD.create(db, task)
    return db_task


@app.get("/api/v1/tasks/{task_id}", response_model=schemas.TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """获取任务"""
    db_task = crud.TaskCRUD.get_by_id(db, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return db_task


@app.get("/api/v1/projects/{project_id}/tasks")
async def list_tasks(
    project_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取项目的任务列表"""
    tasks, total = crud.TaskCRUD.list_by_project(db, project_id, skip, limit)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tasks
    }


# ==================== 知识资产API ====================

@app.post("/api/v1/knowledge-assets", response_model=schemas.KnowledgeAssetResponse)
async def create_knowledge_asset(
    asset: schemas.KnowledgeAssetCreate,
    db: Session = Depends(get_db)
):
    """创建知识资产"""
    db_asset = crud.KnowledgeAssetCRUD.create(db, asset)
    return db_asset


@app.get("/api/v1/knowledge-assets/{asset_id}", response_model=schemas.KnowledgeAssetResponse)
async def get_knowledge_asset(asset_id: str, db: Session = Depends(get_db)):
    """获取知识资产"""
    db_asset = crud.KnowledgeAssetCRUD.get_by_id(db, asset_id)
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识资产不存在"
        )
    return db_asset


@app.get("/api/v1/knowledge-assets")
async def list_knowledge_assets(
    asset_type: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取知识资产列表"""
    if asset_type:
        assets, total = crud.KnowledgeAssetCRUD.list_by_type(
            db, asset_type, skip, limit
        )
    else:
        # 获取所有资产
        query = db.query(models.KnowledgeAsset)
        total = query.count()
        assets = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": assets
    }


# ==================== 仪表板API ====================

@app.get("/api/v1/users/{user_id}/dashboard")
async def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    """获取仪表板数据"""
    # 获取统计数据
    opportunities_count = db.query(models.Opportunity).filter(
        models.Opportunity.user_id == user_id
    ).count()
    
    applications_count = db.query(models.Application).join(
        models.Opportunity
    ).filter(
        models.Opportunity.user_id == user_id
    ).count()
    
    projects_count = db.query(models.Project).filter(
        models.Project.user_id == user_id
    ).count()
    
    knowledge_assets_count = db.query(models.KnowledgeAsset).join(
        models.Project
    ).filter(
        models.Project.user_id == user_id
    ).count()
    
    # 获取最近的机会和项目
    recent_opportunities, _ = crud.OpportunityCRUD.list_by_user(
        db, user_id, 0, 5
    )
    recent_projects, _ = crud.ProjectCRUD.list_by_user(
        db, user_id, 0, 5
    )
    
    return {
        "total_opportunities": opportunities_count,
        "total_applications": applications_count,
        "total_projects": projects_count,
        "knowledge_assets_count": knowledge_assets_count,
        "recent_opportunities": recent_opportunities,
        "recent_projects": recent_projects
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower()
    )
