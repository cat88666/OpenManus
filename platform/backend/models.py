"""
数据库模型定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_data = Column(JSON, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    opportunities = relationship("Opportunity", back_populates="user")
    projects = relationship("Project", back_populates="user")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )


class Opportunity(Base):
    """机会模型"""
    __tablename__ = "opportunities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # upwork, linkedin, toptal
    external_id = Column(String(255), unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    tech_stack = Column(JSON, nullable=True)
    client_id = Column(String(255), nullable=True)
    client_rating = Column(Float, nullable=True)
    proposal_count = Column(Integer, nullable=True)
    ai_score = Column(Float, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    human_review = Column(Text, nullable=True)
    status = Column(String(50), default="discovered")  # discovered, reviewed, applied, won, rejected
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="opportunities")
    applications = relationship("Application", back_populates="opportunity")
    projects = relationship("Project", back_populates="opportunity")
    
    __table_args__ = (
        Index('idx_opportunity_platform_status', 'platform', 'status'),
        Index('idx_opportunity_ai_score', 'ai_score'),
        Index('idx_opportunity_user_id', 'user_id'),
    )


class Application(Base):
    """申请记录模型"""
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=False)
    proposal_text = Column(Text, nullable=False)
    proposed_budget = Column(Float, nullable=True)
    status = Column(String(50), default="sent")  # sent, viewed, rejected, accepted
    sent_at = Column(DateTime, default=datetime.utcnow)
    response_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    opportunity = relationship("Opportunity", back_populates="applications")
    
    __table_args__ = (
        Index('idx_application_opportunity_id', 'opportunity_id'),
        Index('idx_application_status', 'status'),
    )


class Project(Base):
    """项目模型"""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    deliverables = Column(JSON, nullable=True)
    status = Column(String(50), default="in_progress")  # in_progress, review, delivered, paid
    budget = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    client_id = Column(String(255), nullable=True)
    git_repo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="projects")
    opportunity = relationship("Opportunity", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    knowledge_assets = relationship("KnowledgeAsset", back_populates="project")
    
    __table_args__ = (
        Index('idx_project_status', 'status'),
        Index('idx_project_deadline', 'deadline'),
        Index('idx_project_user_id', 'user_id'),
    )


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo")  # todo, in_progress, done
    priority = Column(String(20), default="medium")  # low, medium, high
    assigned_to = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    
    __table_args__ = (
        Index('idx_task_project_id', 'project_id'),
        Index('idx_task_status', 'status'),
    )


class KnowledgeAsset(Base):
    """知识资产模型"""
    __tablename__ = "knowledge_assets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    asset_type = Column(String(50), nullable=False)  # code, doc, template, workflow
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)  # python, javascript, etc
    tech_tags = Column(JSON, nullable=True)
    quality_score = Column(Float, default=0.0)
    reuse_count = Column(Integer, default=0)
    embedding = Column(JSON, nullable=True)  # 向量embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="knowledge_assets")
    
    __table_args__ = (
        Index('idx_knowledge_asset_type', 'asset_type'),
        Index('idx_knowledge_quality_score', 'quality_score'),
        Index('idx_knowledge_project_id', 'project_id'),
    )


class Analytics(Base):
    """分析数据模型"""
    __tablename__ = "analytics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    metric_type = Column(String(100), nullable=False)  # success_rate, avg_budget, etc
    metric_value = Column(Float, nullable=False)
    period = Column(String(50), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_analytics_metric_type', 'metric_type'),
        Index('idx_analytics_period', 'period'),
        Index('idx_analytics_user_id', 'user_id'),
    )
