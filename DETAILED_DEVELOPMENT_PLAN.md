# AI数字员工平台 - 详细开发计划

## 第一部分：架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                   AI数字员工平台                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              前端层 (Frontend)                        │   │
│  │  ├─ React SPA (Web)                                 │   │
│  │  ├─ Streamlit Dashboard (快速原型)                  │   │
│  │  └─ Mobile App (React Native) [后期]               │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API层 (Backend API)                      │   │
│  │  ├─ FastAPI REST API                                │   │
│  │  ├─ WebSocket (实时通知)                            │   │
│  │  └─ GraphQL [后期]                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           业务逻辑层 (Business Logic)                 │   │
│  │  ├─ Oracle (接单引擎)                               │   │
│  │  ├─ Delivery (交付管理)                             │   │
│  │  ├─ Knowledge (知识库)                              │   │
│  │  ├─ Executor (自动执行)                            │   │
│  │  └─ Analytics (分析统计)                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            数据层 (Data Layer)                        │   │
│  │  ├─ PostgreSQL (主数据库)                           │   │
│  │  ├─ ChromaDB (向量数据库)                           │   │
│  │  ├─ Redis (缓存)                                    │   │
│  │  └─ Git (代码版本控制)                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          外部集成 (External Integration)              │   │
│  │  ├─ Upwork API                                      │   │
│  │  ├─ LinkedIn API                                    │   │
│  │  ├─ Claude API (分析)                               │   │
│  │  ├─ OpenAI API (代码生成)                           │   │
│  │  └─ Email/Telegram (通知)                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 模块划分

```
ai-digital-labor-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI应用入口
│   │   ├── config.py                  # 配置管理
│   │   ├── database.py                # 数据库连接
│   │   ├── dependencies.py            # 依赖注入
│   │   │
│   │   ├── models/                    # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── opportunity.py         # 机会模型
│   │   │   ├── project.py             # 项目模型
│   │   │   ├── knowledge.py           # 知识资产模型
│   │   │   ├── user.py                # 用户模型
│   │   │   └── analytics.py           # 分析数据模型
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── opportunity.py
│   │   │   ├── project.py
│   │   │   └── ...
│   │   │
│   │   ├── crud/                      # 数据库操作
│   │   │   ├── __init__.py
│   │   │   ├── opportunity.py
│   │   │   ├── project.py
│   │   │   └── ...
│   │   │
│   │   ├── api/                       # API路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── opportunities.py   # 机会接口
│   │   │   │   ├── projects.py        # 项目接口
│   │   │   │   ├── knowledge.py       # 知识库接口
│   │   │   │   ├── analytics.py       # 分析接口
│   │   │   │   └── users.py           # 用户接口
│   │   │   └── websocket.py           # WebSocket接口
│   │   │
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── oracle/                # 接单引擎
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scraper.py         # 抓取器
│   │   │   │   ├── analyzer.py        # 分析器
│   │   │   │   ├── bidder.py          # 申请管理
│   │   │   │   └── tracker.py         # 跟踪器
│   │   │   │
│   │   │   ├── delivery/              # 交付管理
│   │   │   │   ├── __init__.py
│   │   │   │   ├── project_manager.py
│   │   │   │   ├── quality_checker.py
│   │   │   │   └── communicator.py
│   │   │   │
│   │   │   ├── knowledge/             # 知识库
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_manager.py
│   │   │   │   ├── vector_search.py
│   │   │   │   └── code_analyzer.py
│   │   │   │
│   │   │   ├── executor/              # 自动执行
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auto_coder.py
│   │   │   │   ├── code_generator.py
│   │   │   │   └── test_runner.py
│   │   │   │
│   │   │   └── analytics/             # 分析统计
│   │   │       ├── __init__.py
│   │   │       ├── metrics.py
│   │   │       └── reports.py
│   │   │
│   │   ├── utils/                     # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── llm.py                 # LLM调用
│   │   │   ├── browser.py             # 浏览器自动化
│   │   │   ├── git.py                 # Git操作
│   │   │   ├── email.py               # 邮件发送
│   │   │   └── logger.py              # 日志
│   │   │
│   │   └── tasks/                     # 异步任务
│   │       ├── __init__.py
│   │       ├── scraping.py            # 抓取任务
│   │       ├── analysis.py            # 分析任务
│   │       └── notification.py        # 通知任务
│   │
│   ├── tests/                         # 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_utils/
│   │
│   ├── migrations/                    # 数据库迁移
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── OpportunityBoard.tsx
│   │   │   ├── ProjectDashboard.tsx
│   │   │   ├── KnowledgeBase.tsx
│   │   │   └── Analytics.tsx
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── styles/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── streamlit-dashboard/
│   ├── app.py                         # Streamlit应用
│   ├── pages/
│   │   ├── opportunities.py
│   │   ├── projects.py
│   │   ├── knowledge.py
│   │   └── analytics.py
│   └── requirements.txt
│
├── docker-compose.yml
├── .gitignore
├── README.md
└── DEVELOPMENT_PLAN.md
```

### 1.3 数据库设计

#### 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 机会表
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,  -- upwork, linkedin, toptal
    external_id VARCHAR(255) UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    budget DECIMAL(10, 2),
    currency VARCHAR(3),
    tech_stack JSONB,
    client_id VARCHAR(255),
    client_rating DECIMAL(3, 2),
    proposal_count INTEGER,
    ai_score DECIMAL(3, 2),
    ai_analysis JSONB,
    human_review TEXT,
    status VARCHAR(50),  -- discovered, reviewed, applied, won, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform_status (platform, status),
    INDEX idx_ai_score (ai_score DESC)
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_date TIMESTAMP,
    deadline TIMESTAMP,
    deliverables JSONB,
    status VARCHAR(50),  -- in_progress, review, delivered, paid
    budget DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    client_id VARCHAR(255),
    git_repo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_deadline (deadline)
);

-- 知识资产表
CREATE TABLE knowledge_assets (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    asset_type VARCHAR(50),  -- code, doc, template, workflow
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(50),  -- python, javascript, etc
    tech_tags JSONB,
    quality_score DECIMAL(3, 2),
    reuse_count INTEGER DEFAULT 0,
    embedding VECTOR(1536),  -- 用于向量搜索
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_type (asset_type),
    INDEX idx_quality_score (quality_score DESC)
);

-- 申请记录表
CREATE TABLE applications (
    id UUID PRIMARY KEY,
    opportunity_id UUID REFERENCES opportunities(id),
    proposal_text TEXT NOT NULL,
    proposed_budget DECIMAL(10, 2),
    status VARCHAR(50),  -- sent, viewed, rejected, accepted
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 任务表
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50),  -- todo, in_progress, done
    priority VARCHAR(20),  -- low, medium, high
    assigned_to VARCHAR(255),
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分析数据表
CREATE TABLE analytics (
    id UUID PRIMARY KEY,
    metric_type VARCHAR(100),  -- success_rate, avg_budget, etc
    metric_value DECIMAL(10, 2),
    period VARCHAR(50),  -- daily, weekly, monthly
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 第二部分：开发任务清单

### Phase 1：接单引擎（Week 1-2）

#### Task 1.1：完善Upwork抓取器
- [ ] 增强错误处理和重试机制
- [ ] 实现代理轮换
- [ ] 提取完整字段（客户评价、申请数等）
- [ ] 添加日志系统
- [ ] 实现数据验证
- [ ] 编写单元测试

#### Task 1.2：实现LLM智能评分
- [ ] 设计评分Prompt
- [ ] 集成Claude API
- [ ] 实现5维度评分（预算、技术、需求、客户、竞争）
- [ ] 缓存评分结果
- [ ] 添加反馈调整机制

#### Task 1.3：构建Web Dashboard
- [ ] Streamlit快速原型
- [ ] 展示Top 10机会
- [ ] 实现机会详情展示
- [ ] 添加申请记录
- [ ] 实现基本过滤功能

#### Task 1.4：每日自动运行
- [ ] 实现Celery任务队列
- [ ] 配置定时抓取
- [ ] 实现邮件推送
- [ ] 实现Telegram推送
- [ ] 监控和告警

#### Task 1.5：申请跟踪系统
- [ ] 记录申请状态
- [ ] 跟踪回复率
- [ ] 计算转化率
- [ ] 生成每日报告

### Phase 2：交付管理（Week 3-4）

#### Task 2.1：项目管理系统
- [ ] 项目创建和初始化
- [ ] Git仓库自动创建
- [ ] 任务清单管理
- [ ] 里程碑跟踪
- [ ] 进度报告

#### Task 2.2：知识库系统
- [ ] ChromaDB集成
- [ ] 代码资产自动保存
- [ ] 向量搜索实现
- [ ] 元数据管理
- [ ] 资产评分系统

#### Task 2.3：标准化交付流程
- [ ] 项目结构模板
- [ ] 代码规范指南
- [ ] 文档模板
- [ ] 测试框架
- [ ] 部署脚本

#### Task 2.4：客户沟通系统
- [ ] 沟通模板库
- [ ] 自动回复系统
- [ ] 进度更新自动化
- [ ] 反馈收集系统

### Phase 3：AI辅助（Week 5-6）

#### Task 3.1：代码补全系统
- [ ] 知识库检索集成
- [ ] LLM代码建议
- [ ] 多方案生成
- [ ] 代码质量评分

#### Task 3.2：模板生成
- [ ] 项目类型识别
- [ ] 脚手架生成
- [ ] 依赖配置
- [ ] 工具集成

#### Task 3.3：文档自动生成
- [ ] README生成
- [ ] API文档生成
- [ ] 代码注释优化
- [ ] 架构文档生成

### Phase 4：自动化执行（Week 7-8）

#### Task 4.1：自动编码器
- [ ] 需求理解
- [ ] 任务拆解
- [ ] 代码生成
- [ ] 自动测试
- [ ] 质量检查

#### Task 4.2：质量保证
- [ ] 单元测试自动化
- [ ] 集成测试自动化
- [ ] 代码审查自动化
- [ ] 性能检查

#### Task 4.3：反馈学习
- [ ] 成功案例学习
- [ ] 失败案例分析
- [ ] 模型优化
- [ ] 提示词优化

## 第三部分：技术实现细节

### 3.1 Upwork抓取实现

```python
# app/services/oracle/scraper.py

class UpworkScraper:
    """Upwork职位抓取器"""
    
    def __init__(self):
        self.db = OpportunityDB()
        self.llm = LLMClient()
        self.proxy_manager = ProxyManager()
    
    async def scrape_jobs(self, keywords: List[str], filters: Dict):
        """
        抓取流程：
        1. 构建搜索URL
        2. 使用代理轮换
        3. 解析页面
        4. 提取数据
        5. 数据验证
        6. 存储到数据库
        """
        pass
    
    def parse_job_posting(self, html: str) -> JobOpportunity:
        """解析职位页面"""
        pass
    
    async def get_client_info(self, client_id: str) -> Dict:
        """获取客户信息"""
        pass
```

### 3.2 LLM评分实现

```python
# app/services/oracle/analyzer.py

class OpportunityAnalyzer:
    """机会分析器"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.cache = RedisCache()
    
    async def analyze(self, opportunity: JobOpportunity) -> AnalysisResult:
        """
        分析维度：
        1. 预算合理性（0-20分）
        2. 技术栈匹配（0-25分）
        3. 需求明确度（0-20分）
        4. 客户质量（0-20分）
        5. 竞争程度（0-15分）
        """
        
        prompt = self._build_prompt(opportunity)
        result = await self.llm.analyze(prompt)
        
        # 缓存结果
        self.cache.set(f"analysis:{opportunity.id}", result)
        
        return result
    
    def _build_prompt(self, opportunity: JobOpportunity) -> str:
        """构建分析提示词"""
        return f"""
        分析以下外包机会，给出0-100分的评分：
        
        标题：{opportunity.title}
        预算：${opportunity.budget}
        技术栈：{', '.join(opportunity.tech_stack)}
        客户评价：{opportunity.client_rating}/5
        当前申请数：{opportunity.proposal_count}
        
        我的技能：React, Python, FastAPI, Node.js
        
        请评估：
        1. 是否值得申请？
        2. 风险点？
        3. 建议出价？
        
        输出JSON格式。
        """
```

### 3.3 知识库实现

```python
# app/services/knowledge/asset_manager.py

class KnowledgeAssetManager:
    """知识资产管理器"""
    
    def __init__(self):
        self.vector_db = ChromaDB()
        self.sql_db = SQLiteDB()
        self.git_repo = GitRepository()
    
    async def add_asset(self, project: Project, asset: CodeAsset):
        """
        添加知识资产：
        1. 提取代码片段
        2. 生成embedding
        3. 关联元数据
        4. 存储到数据库
        """
        
        # 生成embedding
        embedding = await self._generate_embedding(asset.content)
        
        # 存储到向量数据库
        self.vector_db.add(
            id=asset.id,
            embedding=embedding,
            metadata={
                'project_id': project.id,
                'asset_type': asset.type,
                'tech_tags': asset.tech_tags,
                'quality_score': asset.quality_score,
            }
        )
        
        # 存储到SQL数据库
        self.sql_db.save_asset(asset)
        
        # 提交到Git
        self.git_repo.commit(asset)
    
    async def search(self, query: str, filters: Dict = None) -> List[CodeAsset]:
        """
        搜索相关资产：
        1. 向量相似度搜索
        2. 根据元数据过滤
        3. 按质量排序
        """
        
        # 生成查询embedding
        query_embedding = await self._generate_embedding(query)
        
        # 向量搜索
        results = self.vector_db.search(
            embedding=query_embedding,
            top_k=10
        )
        
        # 过滤和排序
        filtered_results = self._filter_and_sort(results, filters)
        
        return filtered_results
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本embedding"""
        # 使用OpenAI或其他模型
        pass
```

### 3.4 FastAPI应用结构

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import opportunities, projects, knowledge, analytics
from app.tasks import scraping, analysis

app = FastAPI(title="AI Digital Labor Platform")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(opportunities.router, prefix="/api/v1/opportunities")
app.include_router(projects.router, prefix="/api/v1/projects")
app.include_router(knowledge.router, prefix="/api/v1/knowledge")
app.include_router(analytics.router, prefix="/api/v1/analytics")

@app.on_event("startup")
async def startup():
    """应用启动事件"""
    # 初始化数据库
    # 启动后台任务
    pass

@app.on_event("shutdown")
async def shutdown():
    """应用关闭事件"""
    # 清理资源
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 第四部分：部署和运维

### 4.1 Docker部署

```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_labor
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:password@postgres:5432/ai_labor
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  streamlit:
    build: ./streamlit-dashboard
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 4.2 CI/CD流程

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest backend/tests/ --cov=backend/app
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose push

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # 部署脚本
          pass
```

## 第五部分：关键指标和监控

### 5.1 关键性能指标（KPI）

| 指标 | 目标 | 测量方法 |
|------|------|--------|
| 每日机会数 | 50+ | Upwork抓取日志 |
| LLM评分准确率 | >80% | 人工验证 |
| 申请成功率 | >10% | 申请/成功比例 |
| 项目交付率 | 100% | 已交付/已接项目 |
| 客户满意度 | >4.5/5 | 客户评价 |
| 知识库资产数 | 50+ | 资产表统计 |
| 代码复用率 | 40%+ | 复用次数统计 |
| 自动化率 | 70%+ | 自动化任务/总任务 |

### 5.2 监控告警

```python
# app/monitoring/alerts.py

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_service = EmailService()
    
    def check_scraping_health(self):
        """检查抓取健康状态"""
        last_scrape = self.get_last_scrape_time()
        if datetime.now() - last_scrape > timedelta(hours=2):
            self.alert("Scraping failed", "No data scraped in 2 hours")
    
    def check_api_health(self):
        """检查API健康状态"""
        # 检查数据库连接
        # 检查外部API连接
        # 检查缓存连接
        pass
    
    def alert(self, title: str, message: str):
        """发送告警"""
        self.logger.error(f"{title}: {message}")
        self.email_service.send_alert(title, message)
```

---

**版本**：v1.0
**最后更新**：2026-01-13
