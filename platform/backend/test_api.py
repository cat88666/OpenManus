"""
API测试文件
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import Base
import models
import schemas

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestHealth:
    """健康检查测试"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestUser:
    """用户API测试"""
    
    def test_create_user(self):
        response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
    
    def test_create_duplicate_user(self):
        # 创建第一个用户
        client.post(
            "/api/v1/users",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "testpassword123"
            }
        )
        
        # 尝试创建重复的用户
        response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser3",
                "email": "test2@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 400
    
    def test_get_user(self):
        # 创建用户
        create_response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser4",
                "email": "test4@example.com",
                "password": "testpassword123"
            }
        )
        user_id = create_response.json()["id"]
        
        # 获取用户
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser4"
    
    def test_get_nonexistent_user(self):
        response = client.get("/api/v1/users/nonexistent")
        assert response.status_code == 404


class TestOpportunity:
    """机会API测试"""
    
    @pytest.fixture
    def user_id(self):
        response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser5",
                "email": "test5@example.com",
                "password": "testpassword123"
            }
        )
        return response.json()["id"]
    
    def test_create_opportunity(self, user_id):
        response = client.post(
            "/api/v1/opportunities",
            json={
                "title": "React项目",
                "description": "需要开发一个React应用",
                "platform": "upwork",
                "budget": 2000,
                "tech_stack": ["React", "Node.js"]
            },
            params={"user_id": user_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "React项目"
        assert data["platform"] == "upwork"
    
    def test_list_opportunities(self, user_id):
        # 创建多个机会
        for i in range(3):
            client.post(
                "/api/v1/opportunities",
                json={
                    "title": f"项目{i}",
                    "description": f"描述{i}",
                    "platform": "upwork",
                    "budget": 1000 + i * 500,
                    "tech_stack": ["React"]
                },
                params={"user_id": user_id}
            )
        
        # 获取列表
        response = client.get(
            f"/api/v1/users/{user_id}/opportunities",
            params={"skip": 0, "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3


class TestApplication:
    """申请API测试"""
    
    @pytest.fixture
    def setup(self):
        # 创建用户
        user_response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser6",
                "email": "test6@example.com",
                "password": "testpassword123"
            }
        )
        user_id = user_response.json()["id"]
        
        # 创建机会
        opp_response = client.post(
            "/api/v1/opportunities",
            json={
                "title": "测试项目",
                "description": "测试描述",
                "platform": "upwork",
                "budget": 2000,
                "tech_stack": ["React"]
            },
            params={"user_id": user_id}
        )
        opportunity_id = opp_response.json()["id"]
        
        return user_id, opportunity_id
    
    def test_create_application(self, setup):
        user_id, opportunity_id = setup
        
        response = client.post(
            "/api/v1/applications",
            json={
                "opportunity_id": opportunity_id,
                "proposal_text": "我对这个项目很感兴趣，有丰富的React经验",
                "proposed_budget": 1800
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["opportunity_id"] == opportunity_id
        assert data["status"] == "sent"


class TestProject:
    """项目API测试"""
    
    @pytest.fixture
    def user_id(self):
        response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser7",
                "email": "test7@example.com",
                "password": "testpassword123"
            }
        )
        return response.json()["id"]
    
    def test_create_project(self, user_id):
        response = client.post(
            "/api/v1/projects",
            json={
                "title": "测试项目",
                "description": "这是一个测试项目",
                "budget": 3000
            },
            params={"user_id": user_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试项目"
        assert data["status"] == "in_progress"


class TestTask:
    """任务API测试"""
    
    @pytest.fixture
    def project_id(self):
        # 创建用户
        user_response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser8",
                "email": "test8@example.com",
                "password": "testpassword123"
            }
        )
        user_id = user_response.json()["id"]
        
        # 创建项目
        project_response = client.post(
            "/api/v1/projects",
            json={
                "title": "测试项目",
                "description": "测试",
                "budget": 2000
            },
            params={"user_id": user_id}
        )
        return project_response.json()["id"]
    
    def test_create_task(self, project_id):
        response = client.post(
            "/api/v1/tasks",
            json={
                "project_id": project_id,
                "title": "实现登录功能",
                "description": "使用JWT实现用户登录",
                "priority": "high"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "实现登录功能"
        assert data["status"] == "todo"


class TestKnowledgeAsset:
    """知识资产API测试"""
    
    def test_create_knowledge_asset(self):
        response = client.post(
            "/api/v1/knowledge-assets",
            json={
                "title": "React Hook最佳实践",
                "content": "const useCustomHook = () => { ... }",
                "asset_type": "code",
                "language": "javascript",
                "tech_tags": ["React", "Hooks"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "React Hook最佳实践"
        assert data["asset_type"] == "code"


class TestDashboard:
    """仪表板API测试"""
    
    def test_get_dashboard(self):
        # 创建用户
        user_response = client.post(
            "/api/v1/users",
            json={
                "username": "testuser9",
                "email": "test9@example.com",
                "password": "testpassword123"
            }
        )
        user_id = user_response.json()["id"]
        
        # 获取仪表板
        response = client.get(f"/api/v1/users/{user_id}/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_opportunities" in data
        assert "total_applications" in data
        assert "total_projects" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
