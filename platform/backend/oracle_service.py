"""
Oracle服务 - 接单引擎核心模块
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
import schemas
import crud
from llm_service import get_llm_service

logger = logging.getLogger(__name__)


class OracleService:
    """接单引擎服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = get_llm_service("openai")
    
    async def scrape_opportunities(
        self,
        user_id: str,
        platforms: List[str] = None,
        keywords: List[str] = None
    ) -> List[models.Opportunity]:
        """
        从多个平台抓取机会
        
        Args:
            user_id: 用户ID
            platforms: 平台列表 (upwork, linkedin, toptal)
            keywords: 搜索关键词
        
        Returns:
            机会列表
        """
        if not platforms:
            platforms = ["upwork", "linkedin"]
        
        if not keywords:
            keywords = ["React", "Python", "Node.js", "FastAPI"]
        
        opportunities = []
        
        for platform in platforms:
            try:
                if platform == "upwork":
                    platform_opportunities = await self._scrape_upwork(keywords)
                elif platform == "linkedin":
                    platform_opportunities = await self._scrape_linkedin(keywords)
                elif platform == "toptal":
                    platform_opportunities = await self._scrape_toptal(keywords)
                else:
                    continue
                
                # 保存机会到数据库
                for opp_data in platform_opportunities:
                    existing = crud.OpportunityCRUD.get_by_external_id(
                        self.db, opp_data.get("external_id")
                    )
                    
                    if not existing:
                        opportunity = schemas.OpportunityCreate(
                            title=opp_data.get("title"),
                            description=opp_data.get("description"),
                            platform=platform,
                            budget=opp_data.get("budget"),
                            tech_stack=opp_data.get("tech_stack", []),
                            client_id=opp_data.get("client_id"),
                            client_rating=opp_data.get("client_rating"),
                            proposal_count=opp_data.get("proposal_count"),
                            external_id=opp_data.get("external_id"),
                            url=opp_data.get("url")
                        )
                        
                        db_opportunity = crud.OpportunityCRUD.create(
                            self.db, opportunity, user_id
                        )
                        opportunities.append(db_opportunity)
                        
                        logger.info(f"新机会已保存: {db_opportunity.title}")
            
            except Exception as e:
                logger.error(f"从{platform}抓取失败: {e}")
                continue
        
        return opportunities
    
    async def analyze_opportunities(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        分析用户的机会
        
        Args:
            user_id: 用户ID
            limit: 分析数量限制
        
        Returns:
            分析结果列表
        """
        # 获取未分析的机会
        opportunities, _ = crud.OpportunityCRUD.list_by_user(
            self.db,
            user_id,
            skip=0,
            limit=limit,
            status="discovered"
        )
        
        results = []
        
        for opportunity in opportunities:
            try:
                # 检查是否已分析
                if opportunity.ai_score is not None:
                    continue
                
                # 构建分析数据
                opportunity_data = {
                    "title": opportunity.title,
                    "description": opportunity.description,
                    "budget": opportunity.budget,
                    "tech_stack": opportunity.tech_stack or [],
                    "client_rating": opportunity.client_rating,
                    "proposal_count": opportunity.proposal_count
                }
                
                # 调用LLM分析
                analysis = await self.llm_service.analyze_opportunity(opportunity_data)
                
                # 更新机会
                update_data = schemas.OpportunityUpdate(
                    ai_score=analysis.get("score"),
                    ai_analysis=analysis,
                    status="reviewed"
                )
                
                updated_opportunity = crud.OpportunityCRUD.update(
                    self.db,
                    opportunity.id,
                    update_data
                )
                
                results.append({
                    "opportunity_id": opportunity.id,
                    "title": opportunity.title,
                    "score": analysis.get("score"),
                    "analysis": analysis
                })
                
                logger.info(f"机会已分析: {opportunity.title} (评分: {analysis.get('score')})")
            
            except Exception as e:
                logger.error(f"分析机会失败: {e}")
                continue
        
        return results
    
    async def generate_proposal(
        self,
        opportunity_id: str
    ) -> str:
        """
        为机会生成申请信
        
        Args:
            opportunity_id: 机会ID
        
        Returns:
            申请信文本
        """
        opportunity = crud.OpportunityCRUD.get_by_id(self.db, opportunity_id)
        
        if not opportunity:
            raise ValueError(f"机会不存在: {opportunity_id}")
        
        opportunity_data = {
            "title": opportunity.title,
            "description": opportunity.description,
            "budget": opportunity.budget,
            "tech_stack": opportunity.tech_stack or [],
            "client_rating": opportunity.client_rating
        }
        
        proposal = await self.llm_service.generate_proposal(opportunity_data)
        
        return proposal
    
    async def submit_application(
        self,
        opportunity_id: str,
        proposal_text: str,
        proposed_budget: Optional[float] = None
    ) -> models.Application:
        """
        提交申请
        
        Args:
            opportunity_id: 机会ID
            proposal_text: 申请信文本
            proposed_budget: 提议预算
        
        Returns:
            申请记录
        """
        application = schemas.ApplicationCreate(
            opportunity_id=opportunity_id,
            proposal_text=proposal_text,
            proposed_budget=proposed_budget
        )
        
        db_application = crud.ApplicationCRUD.create(self.db, application)
        
        # 更新机会状态
        update_data = schemas.OpportunityUpdate(status="applied")
        crud.OpportunityCRUD.update(self.db, opportunity_id, update_data)
        
        logger.info(f"申请已提交: {opportunity_id}")
        
        return db_application
    
    async def get_top_opportunities(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[models.Opportunity]:
        """
        获取评分最高的机会
        
        Args:
            user_id: 用户ID
            limit: 返回数量
        
        Returns:
            机会列表
        """
        return crud.OpportunityCRUD.get_top_opportunities(self.db, user_id, limit)
    
    async def get_application_stats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        获取申请统计
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计数据
        """
        # 获取用户的机会
        opportunities, total_opportunities = crud.OpportunityCRUD.list_by_user(
            self.db, user_id, skip=0, limit=1000
        )
        
        # 统计申请
        total_applications = 0
        successful_applications = 0
        
        for opportunity in opportunities:
            applications, _ = crud.ApplicationCRUD.list_by_opportunity(
                self.db, opportunity.id, skip=0, limit=1000
            )
            total_applications += len(applications)
            
            # 统计成功的申请（状态为accepted）
            successful_applications += sum(
                1 for app in applications if app.status == "accepted"
            )
        
        # 计算转化率
        conversion_rate = (
            (successful_applications / total_applications * 100)
            if total_applications > 0
            else 0
        )
        
        return {
            "total_opportunities": total_opportunities,
            "total_applications": total_applications,
            "successful_applications": successful_applications,
            "conversion_rate": round(conversion_rate, 2),
            "average_applications_per_opportunity": (
                round(total_applications / total_opportunities, 2)
                if total_opportunities > 0
                else 0
            )
        }
    
    # ==================== 内部方法 ====================
    
    async def _scrape_upwork(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        从Upwork抓取机会
        
        注意：这是一个模拟实现。实际应该使用Upwork API或浏览器自动化
        """
        logger.info(f"从Upwork抓取机会: {keywords}")
        
        # 模拟数据
        mock_opportunities = [
            {
                "title": "React + Node.js 全栈项目",
                "description": "需要开发一个React前端和Node.js后端的电商平台",
                "budget": 2500,
                "tech_stack": ["React", "Node.js", "MongoDB"],
                "client_id": "upwork_client_001",
                "client_rating": 4.8,
                "proposal_count": 15,
                "external_id": "upwork_job_001",
                "url": "https://upwork.com/jobs/001"
            },
            {
                "title": "Python FastAPI API开发",
                "description": "需要开发一个高性能的REST API",
                "budget": 1500,
                "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
                "client_id": "upwork_client_002",
                "client_rating": 4.5,
                "proposal_count": 8,
                "external_id": "upwork_job_002",
                "url": "https://upwork.com/jobs/002"
            }
        ]
        
        return mock_opportunities
    
    async def _scrape_linkedin(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        从LinkedIn抓取机会
        """
        logger.info(f"从LinkedIn抓取机会: {keywords}")
        
        # 模拟数据
        mock_opportunities = [
            {
                "title": "远程前端开发工程师",
                "description": "寻找有经验的React开发者",
                "budget": 3000,
                "tech_stack": ["React", "TypeScript", "TailwindCSS"],
                "client_id": "linkedin_client_001",
                "client_rating": 4.7,
                "proposal_count": 20,
                "external_id": "linkedin_job_001",
                "url": "https://linkedin.com/jobs/001"
            }
        ]
        
        return mock_opportunities
    
    async def _scrape_toptal(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        从Toptal抓取机会
        """
        logger.info(f"从Toptal抓取机会: {keywords}")
        
        # 模拟数据
        mock_opportunities = []
        
        return mock_opportunities


class KnowledgeBaseService:
    """知识库服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def add_asset_from_project(
        self,
        project_id: str,
        asset_type: str,
        title: str,
        content: str,
        language: Optional[str] = None,
        tech_tags: Optional[List[str]] = None
    ) -> models.KnowledgeAsset:
        """
        从项目添加知识资产
        
        Args:
            project_id: 项目ID
            asset_type: 资产类型 (code, doc, template, workflow)
            title: 资产标题
            content: 资产内容
            language: 编程语言
            tech_tags: 技术标签
        
        Returns:
            知识资产
        """
        asset = schemas.KnowledgeAssetCreate(
            project_id=project_id,
            asset_type=asset_type,
            title=title,
            content=content,
            language=language,
            tech_tags=tech_tags or []
        )
        
        db_asset = crud.KnowledgeAssetCRUD.create(self.db, asset)
        
        logger.info(f"知识资产已添加: {title}")
        
        return db_asset
    
    async def search_similar_assets(
        self,
        query: str,
        asset_type: Optional[str] = None,
        limit: int = 5
    ) -> List[models.KnowledgeAsset]:
        """
        搜索相似的知识资产
        
        Args:
            query: 搜索查询
            asset_type: 资产类型过滤
            limit: 返回数量
        
        Returns:
            相似资产列表
        """
        # 简单的文本搜索实现
        # 实际应该使用向量搜索和ChromaDB
        
        if asset_type:
            assets, _ = crud.KnowledgeAssetCRUD.list_by_type(
                self.db, asset_type, skip=0, limit=limit
            )
        else:
            query_result = self.db.query(models.KnowledgeAsset)
            assets = query_result.limit(limit).all()
        
        return assets
    
    async def update_asset_quality(
        self,
        asset_id: str,
        quality_score: float
    ) -> Optional[models.KnowledgeAsset]:
        """
        更新资产质量评分
        
        Args:
            asset_id: 资产ID
            quality_score: 质量评分 (0-1)
        
        Returns:
            更新后的资产
        """
        update_data = schemas.KnowledgeAssetUpdate(
            quality_score=quality_score
        )
        
        return crud.KnowledgeAssetCRUD.update(self.db, asset_id, update_data)
    
    async def increment_reuse_count(self, asset_id: str) -> Optional[models.KnowledgeAsset]:
        """
        增加资产复用次数
        
        Args:
            asset_id: 资产ID
        
        Returns:
            更新后的资产
        """
        asset = crud.KnowledgeAssetCRUD.get_by_id(self.db, asset_id)
        
        if asset:
            update_data = schemas.KnowledgeAssetUpdate(
                reuse_count=asset.reuse_count + 1
            )
            return crud.KnowledgeAssetCRUD.update(self.db, asset_id, update_data)
        
        return None


class DeliveryService:
    """交付管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_project_from_opportunity(
        self,
        opportunity_id: str,
        user_id: str
    ) -> models.Project:
        """
        从机会创建项目
        
        Args:
            opportunity_id: 机会ID
            user_id: 用户ID
        
        Returns:
            项目
        """
        opportunity = crud.OpportunityCRUD.get_by_id(self.db, opportunity_id)
        
        if not opportunity:
            raise ValueError(f"机会不存在: {opportunity_id}")
        
        project = schemas.ProjectCreate(
            title=opportunity.title,
            description=opportunity.description,
            budget=opportunity.budget,
            opportunity_id=opportunity_id
        )
        
        db_project = crud.ProjectCRUD.create(self.db, project, user_id)
        
        logger.info(f"项目已创建: {db_project.title}")
        
        return db_project
    
    async def create_task(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None
    ) -> models.Task:
        """
        创建项目任务
        
        Args:
            project_id: 项目ID
            title: 任务标题
            description: 任务描述
            priority: 优先级
            due_date: 截止日期
        
        Returns:
            任务
        """
        task = schemas.TaskCreate(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        db_task = crud.TaskCRUD.create(self.db, task)
        
        logger.info(f"任务已创建: {title}")
        
        return db_task
    
    async def update_task_status(
        self,
        task_id: str,
        status: str
    ) -> Optional[models.Task]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态 (todo, in_progress, done)
        
        Returns:
            更新后的任务
        """
        update_data = schemas.TaskUpdate(status=status)
        
        return crud.TaskCRUD.update(self.db, task_id, update_data)
    
    async def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """
        获取项目进度
        
        Args:
            project_id: 项目ID
        
        Returns:
            进度数据
        """
        project = crud.ProjectCRUD.get_by_id(self.db, project_id)
        
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        tasks, total_tasks = crud.TaskCRUD.list_by_project(
            self.db, project_id, skip=0, limit=1000
        )
        
        completed_tasks = sum(1 for task in tasks if task.status == "done")
        in_progress_tasks = sum(1 for task in tasks if task.status == "in_progress")
        todo_tasks = sum(1 for task in tasks if task.status == "todo")
        
        progress_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )
        
        return {
            "project_id": project_id,
            "project_title": project.title,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": todo_tasks,
            "progress_percentage": round(progress_percentage, 2),
            "deadline": project.deadline,
            "status": project.status
        }
