"""
CRUD操作模块
"""
from typing import List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
import models
import schemas

T = TypeVar('T')


# ==================== 用户操作 ====================

class UserCRUD:
    @staticmethod
    def create(db: Session, user: schemas.UserCreate) -> models.User:
        """创建用户"""
        db_user = models.User(
            username=user.username,
            email=user.email,
            password_hash=user.password  # 实际应该hash密码
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[models.User]:
        """根据ID获取用户"""
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.User]:
        """根据邮箱获取用户"""
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[models.User]:
        """根据用户名获取用户"""
        return db.query(models.User).filter(models.User.username == username).first()
    
    @staticmethod
    def update(db: Session, user_id: str, user: schemas.UserUpdate) -> Optional[models.User]:
        """更新用户"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete(db: Session, user_id: str) -> bool:
        """删除用户"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False


# ==================== 机会操作 ====================

class OpportunityCRUD:
    @staticmethod
    def create(db: Session, opportunity: schemas.OpportunityCreate, user_id: str) -> models.Opportunity:
        """创建机会"""
        db_opportunity = models.Opportunity(
            user_id=user_id,
            **opportunity.dict()
        )
        db.add(db_opportunity)
        db.commit()
        db.refresh(db_opportunity)
        return db_opportunity
    
    @staticmethod
    def get_by_id(db: Session, opportunity_id: str) -> Optional[models.Opportunity]:
        """根据ID获取机会"""
        return db.query(models.Opportunity).filter(
            models.Opportunity.id == opportunity_id
        ).first()
    
    @staticmethod
    def get_by_external_id(db: Session, external_id: str) -> Optional[models.Opportunity]:
        """根据外部ID获取机会"""
        return db.query(models.Opportunity).filter(
            models.Opportunity.external_id == external_id
        ).first()
    
    @staticmethod
    def list_by_user(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        platform: Optional[str] = None
    ) -> tuple[List[models.Opportunity], int]:
        """获取用户的机会列表"""
        query = db.query(models.Opportunity).filter(
            models.Opportunity.user_id == user_id
        )
        
        if status:
            query = query.filter(models.Opportunity.status == status)
        if platform:
            query = query.filter(models.Opportunity.platform == platform)
        
        total = query.count()
        opportunities = query.order_by(
            desc(models.Opportunity.ai_score)
        ).offset(skip).limit(limit).all()
        
        return opportunities, total
    
    @staticmethod
    def update(db: Session, opportunity_id: str, opportunity: schemas.OpportunityUpdate) -> Optional[models.Opportunity]:
        """更新机会"""
        db_opportunity = OpportunityCRUD.get_by_id(db, opportunity_id)
        if db_opportunity:
            update_data = opportunity.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_opportunity, key, value)
            db.commit()
            db.refresh(db_opportunity)
        return db_opportunity
    
    @staticmethod
    def delete(db: Session, opportunity_id: str) -> bool:
        """删除机会"""
        db_opportunity = OpportunityCRUD.get_by_id(db, opportunity_id)
        if db_opportunity:
            db.delete(db_opportunity)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_top_opportunities(
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[models.Opportunity]:
        """获取评分最高的机会"""
        return db.query(models.Opportunity).filter(
            and_(
                models.Opportunity.user_id == user_id,
                models.Opportunity.status == "discovered"
            )
        ).order_by(
            desc(models.Opportunity.ai_score)
        ).limit(limit).all()


# ==================== 申请操作 ====================

class ApplicationCRUD:
    @staticmethod
    def create(db: Session, application: schemas.ApplicationCreate) -> models.Application:
        """创建申请"""
        db_application = models.Application(**application.dict())
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application
    
    @staticmethod
    def get_by_id(db: Session, application_id: str) -> Optional[models.Application]:
        """根据ID获取申请"""
        return db.query(models.Application).filter(
            models.Application.id == application_id
        ).first()
    
    @staticmethod
    def list_by_opportunity(
        db: Session,
        opportunity_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[models.Application], int]:
        """获取机会的申请列表"""
        query = db.query(models.Application).filter(
            models.Application.opportunity_id == opportunity_id
        )
        total = query.count()
        applications = query.offset(skip).limit(limit).all()
        return applications, total
    
    @staticmethod
    def update(db: Session, application_id: str, application: schemas.ApplicationUpdate) -> Optional[models.Application]:
        """更新申请"""
        db_application = ApplicationCRUD.get_by_id(db, application_id)
        if db_application:
            update_data = application.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_application, key, value)
            db.commit()
            db.refresh(db_application)
        return db_application


# ==================== 项目操作 ====================

class ProjectCRUD:
    @staticmethod
    def create(db: Session, project: schemas.ProjectCreate, user_id: str) -> models.Project:
        """创建项目"""
        db_project = models.Project(
            user_id=user_id,
            **project.dict()
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_by_id(db: Session, project_id: str) -> Optional[models.Project]:
        """根据ID获取项目"""
        return db.query(models.Project).filter(
            models.Project.id == project_id
        ).first()
    
    @staticmethod
    def list_by_user(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> tuple[List[models.Project], int]:
        """获取用户的项目列表"""
        query = db.query(models.Project).filter(
            models.Project.user_id == user_id
        )
        
        if status:
            query = query.filter(models.Project.status == status)
        
        total = query.count()
        projects = query.order_by(
            desc(models.Project.created_at)
        ).offset(skip).limit(limit).all()
        
        return projects, total
    
    @staticmethod
    def update(db: Session, project_id: str, project: schemas.ProjectUpdate) -> Optional[models.Project]:
        """更新项目"""
        db_project = ProjectCRUD.get_by_id(db, project_id)
        if db_project:
            update_data = project.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_project, key, value)
            db.commit()
            db.refresh(db_project)
        return db_project


# ==================== 任务操作 ====================

class TaskCRUD:
    @staticmethod
    def create(db: Session, task: schemas.TaskCreate) -> models.Task:
        """创建任务"""
        db_task = models.Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_by_id(db: Session, task_id: str) -> Optional[models.Task]:
        """根据ID获取任务"""
        return db.query(models.Task).filter(
            models.Task.id == task_id
        ).first()
    
    @staticmethod
    def list_by_project(
        db: Session,
        project_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[models.Task], int]:
        """获取项目的任务列表"""
        query = db.query(models.Task).filter(
            models.Task.project_id == project_id
        )
        total = query.count()
        tasks = query.offset(skip).limit(limit).all()
        return tasks, total
    
    @staticmethod
    def update(db: Session, task_id: str, task: schemas.TaskUpdate) -> Optional[models.Task]:
        """更新任务"""
        db_task = TaskCRUD.get_by_id(db, task_id)
        if db_task:
            update_data = task.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task, key, value)
            db.commit()
            db.refresh(db_task)
        return db_task


# ==================== 知识资产操作 ====================

class KnowledgeAssetCRUD:
    @staticmethod
    def create(db: Session, asset: schemas.KnowledgeAssetCreate) -> models.KnowledgeAsset:
        """创建知识资产"""
        db_asset = models.KnowledgeAsset(**asset.dict())
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    
    @staticmethod
    def get_by_id(db: Session, asset_id: str) -> Optional[models.KnowledgeAsset]:
        """根据ID获取知识资产"""
        return db.query(models.KnowledgeAsset).filter(
            models.KnowledgeAsset.id == asset_id
        ).first()
    
    @staticmethod
    def list_by_type(
        db: Session,
        asset_type: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[models.KnowledgeAsset], int]:
        """按类型获取知识资产"""
        query = db.query(models.KnowledgeAsset).filter(
            models.KnowledgeAsset.asset_type == asset_type
        )
        total = query.count()
        assets = query.order_by(
            desc(models.KnowledgeAsset.quality_score)
        ).offset(skip).limit(limit).all()
        return assets, total
    
    @staticmethod
    def update(db: Session, asset_id: str, asset: schemas.KnowledgeAssetUpdate) -> Optional[models.KnowledgeAsset]:
        """更新知识资产"""
        db_asset = KnowledgeAssetCRUD.get_by_id(db, asset_id)
        if db_asset:
            update_data = asset.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_asset, key, value)
            db.commit()
            db.refresh(db_asset)
        return db_asset
