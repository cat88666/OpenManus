"""
集成测试脚本
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from database import Base
import models
import schemas
import crud
from oracle_service import OracleService, DeliveryService, KnowledgeBaseService

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库会话"""
        connection = engine.connect()
        transaction = connection.begin()
        session = TestingSessionLocal(bind=connection)
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()
    
    def test_user_creation_and_retrieval(self, db):
        """测试用户创建和检索"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        
        db_user = crud.UserCRUD.create(db, user_data)
        assert db_user.id is not None
        assert db_user.username == "testuser"
        assert db_user.email == "test@example.com"
        
        # 检索用户
        retrieved_user = crud.UserCRUD.get_by_id(db, db_user.id)
        assert retrieved_user.id == db_user.id
        assert retrieved_user.username == "testuser"
    
    def test_opportunity_creation_and_analysis(self, db):
        """测试机会创建和分析"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser2",
            email="test2@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 创建机会
        opportunity_data = schemas.OpportunityCreate(
            title="React项目",
            description="需要开发一个React应用",
            platform="upwork",
            budget=2000,
            tech_stack=["React", "Node.js"]
        )
        
        db_opportunity = crud.OpportunityCRUD.create(db, opportunity_data, db_user.id)
        assert db_opportunity.id is not None
        assert db_opportunity.title == "React项目"
        assert db_opportunity.status == "discovered"
        
        # 检索机会
        retrieved_opportunity = crud.OpportunityCRUD.get_by_id(db, db_opportunity.id)
        assert retrieved_opportunity.id == db_opportunity.id
    
    def test_application_workflow(self, db):
        """测试申请工作流"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser3",
            email="test3@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 创建机会
        opportunity_data = schemas.OpportunityCreate(
            title="测试项目",
            description="测试描述",
            platform="upwork",
            budget=1500
        )
        db_opportunity = crud.OpportunityCRUD.create(db, opportunity_data, db_user.id)
        
        # 创建申请
        application_data = schemas.ApplicationCreate(
            opportunity_id=db_opportunity.id,
            proposal_text="我对这个项目很感兴趣",
            proposed_budget=1400
        )
        
        db_application = crud.ApplicationCRUD.create(db, application_data)
        assert db_application.id is not None
        assert db_application.status == "sent"
        
        # 更新申请状态
        update_data = schemas.ApplicationUpdate(status="accepted")
        updated_application = crud.ApplicationCRUD.update(db, db_application.id, update_data)
        assert updated_application.status == "accepted"
    
    def test_project_and_task_workflow(self, db):
        """测试项目和任务工作流"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser4",
            email="test4@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 创建项目
        project_data = schemas.ProjectCreate(
            title="测试项目",
            description="这是一个测试项目",
            budget=3000
        )
        
        db_project = crud.ProjectCRUD.create(db, project_data, db_user.id)
        assert db_project.id is not None
        assert db_project.status == "in_progress"
        
        # 创建任务
        task_data = schemas.TaskCreate(
            project_id=db_project.id,
            title="实现登录功能",
            description="使用JWT实现用户登录",
            priority="high"
        )
        
        db_task = crud.TaskCRUD.create(db, task_data)
        assert db_task.id is not None
        assert db_task.status == "todo"
        
        # 更新任务状态
        update_data = schemas.TaskUpdate(status="in_progress")
        updated_task = crud.TaskCRUD.update(db, db_task.id, update_data)
        assert updated_task.status == "in_progress"
    
    def test_knowledge_asset_workflow(self, db):
        """测试知识资产工作流"""
        # 创建知识资产
        asset_data = schemas.KnowledgeAssetCreate(
            title="React Hook最佳实践",
            content="const useCustomHook = () => { ... }",
            asset_type="code",
            language="javascript",
            tech_tags=["React", "Hooks"]
        )
        
        db_asset = crud.KnowledgeAssetCRUD.create(db, asset_data)
        assert db_asset.id is not None
        assert db_asset.asset_type == "code"
        assert db_asset.quality_score == 0.5  # 默认质量评分
        
        # 更新质量评分
        update_data = schemas.KnowledgeAssetUpdate(quality_score=0.9)
        updated_asset = crud.KnowledgeAssetCRUD.update(db, db_asset.id, update_data)
        assert updated_asset.quality_score == 0.9
    
    @pytest.mark.asyncio
    async def test_oracle_service_workflow(self, db):
        """测试Oracle服务工作流"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser5",
            email="test5@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 创建Oracle服务
        oracle_service = OracleService(db)
        
        # 测试获取应用统计
        stats = await oracle_service.get_application_stats(db_user.id)
        assert stats["total_opportunities"] == 0
        assert stats["total_applications"] == 0
        assert stats["conversion_rate"] == 0
    
    @pytest.mark.asyncio
    async def test_delivery_service_workflow(self, db):
        """测试交付服务工作流"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="testuser6",
            email="test6@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 创建机会
        opportunity_data = schemas.OpportunityCreate(
            title="测试项目",
            description="测试描述",
            platform="upwork",
            budget=2000
        )
        db_opportunity = crud.OpportunityCRUD.create(db, opportunity_data, db_user.id)
        
        # 创建交付服务
        delivery_service = DeliveryService(db)
        
        # 从机会创建项目
        db_project = await delivery_service.create_project_from_opportunity(
            db_opportunity.id,
            db_user.id
        )
        assert db_project.id is not None
        assert db_project.title == "测试项目"
        
        # 创建任务
        db_task = await delivery_service.create_task(
            db_project.id,
            "实现功能A",
            "实现功能A的详细描述"
        )
        assert db_task.id is not None
        
        # 获取项目进度
        progress = await delivery_service.get_project_progress(db_project.id)
        assert progress["project_id"] == db_project.id
        assert progress["total_tasks"] == 1
        assert progress["progress_percentage"] == 0
    
    @pytest.mark.asyncio
    async def test_knowledge_base_service_workflow(self, db):
        """测试知识库服务工作流"""
        # 创建知识库服务
        kb_service = KnowledgeBaseService(db)
        
        # 添加资产
        db_asset = await kb_service.add_asset_from_project(
            project_id="test_project",
            asset_type="code",
            title="React组件模板",
            content="export const MyComponent = () => { ... }",
            language="typescript",
            tech_tags=["React", "TypeScript"]
        )
        assert db_asset.id is not None
        
        # 更新质量评分
        updated_asset = await kb_service.update_asset_quality(db_asset.id, 0.95)
        assert updated_asset.quality_score == 0.95
        
        # 增加复用次数
        reused_asset = await kb_service.increment_reuse_count(db_asset.id)
        assert reused_asset.reuse_count == 1


class TestPerformance:
    """性能测试"""
    
    @pytest.fixture
    def db(self):
        """创建测试数据库会话"""
        connection = engine.connect()
        transaction = connection.begin()
        session = TestingSessionLocal(bind=connection)
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()
    
    def test_bulk_opportunity_creation(self, db):
        """测试批量创建机会的性能"""
        # 创建用户
        user_data = schemas.UserCreate(
            username="bulk_test_user",
            email="bulk@example.com",
            password="testpassword123"
        )
        db_user = crud.UserCRUD.create(db, user_data)
        
        # 批量创建机会
        import time
        start_time = time.time()
        
        for i in range(100):
            opportunity_data = schemas.OpportunityCreate(
                title=f"机会{i}",
                description=f"描述{i}",
                platform="upwork",
                budget=1000 + i * 100
            )
            crud.OpportunityCRUD.create(db, opportunity_data, db_user.id)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 验证创建的机会数量
        opportunities, total = crud.OpportunityCRUD.list_by_user(
            db, db_user.id, skip=0, limit=1000
        )
        assert total == 100
        
        # 输出性能信息
        print(f"\n批量创建100个机会耗时: {elapsed_time:.2f}秒")
        print(f"平均每个机会耗时: {elapsed_time/100*1000:.2f}毫秒")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
