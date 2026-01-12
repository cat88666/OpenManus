"""
Pydantic数据模型定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ==================== 用户相关 ====================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_data: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 机会相关 ====================

class OpportunityBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    platform: str
    budget: Optional[float] = None
    currency: str = "USD"
    tech_stack: Optional[List[str]] = None
    client_id: Optional[str] = None
    client_rating: Optional[float] = None
    proposal_count: Optional[int] = None


class OpportunityCreate(OpportunityBase):
    external_id: Optional[str] = None
    url: Optional[str] = None


class OpportunityUpdate(BaseModel):
    ai_score: Optional[float] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    human_review: Optional[str] = None
    status: Optional[str] = None


class OpportunityAnalysis(BaseModel):
    score: float = Field(..., ge=0, le=100)
    reason: str
    recommended_budget: Optional[float] = None
    risks: List[str] = []
    recommendations: List[str] = []


class OpportunityResponse(OpportunityBase):
    id: str
    external_id: Optional[str] = None
    ai_score: Optional[float] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    human_review: Optional[str] = None
    status: str
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 申请相关 ====================

class ApplicationBase(BaseModel):
    proposal_text: str = Field(..., min_length=50)
    proposed_budget: Optional[float] = None


class ApplicationCreate(ApplicationBase):
    opportunity_id: str


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: str
    opportunity_id: str
    status: str
    sent_at: datetime
    response_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 项目相关 ====================

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    deliverables: Optional[List[str]] = None
    budget: Optional[float] = None
    client_id: Optional[str] = None


class ProjectCreate(ProjectBase):
    opportunity_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    actual_cost: Optional[float] = None
    git_repo_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    status: str
    actual_cost: Optional[float] = None
    git_repo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 任务相关 ====================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: str
    project_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 知识资产相关 ====================

class KnowledgeAssetBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    content: str = Field(..., min_length=10)
    asset_type: str
    language: Optional[str] = None
    tech_tags: Optional[List[str]] = None


class KnowledgeAssetCreate(KnowledgeAssetBase):
    project_id: Optional[str] = None


class KnowledgeAssetUpdate(BaseModel):
    quality_score: Optional[float] = None
    reuse_count: Optional[int] = None


class KnowledgeAssetResponse(KnowledgeAssetBase):
    id: str
    project_id: Optional[str] = None
    quality_score: float
    reuse_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 分析相关 ====================

class AnalyticsResponse(BaseModel):
    id: str
    metric_type: str
    metric_value: float
    period: str
    period_start: datetime
    period_end: datetime
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    total_opportunities: int
    total_applications: int
    total_projects: int
    success_rate: float
    average_budget: float
    total_revenue: float
    knowledge_assets_count: int
    recent_opportunities: List[OpportunityResponse]
    recent_projects: List[ProjectResponse]


# ==================== 分页相关 ====================

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[Any]
