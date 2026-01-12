# AI数字员工平台

一个智能的AI跨境数字劳务外包平台，帮助自由职业者自动化接单、交付和知识积累的全流程。

## 📋 项目概述

### 核心功能

1. **The Oracle（接单引擎）**
   - 自动从Upwork、LinkedIn、Toptal抓取外包机会
   - 使用LLM智能评分和筛选
   - 生成个性化的申请信
   - 跟踪申请状态和转化率

2. **交付管理**
   - 项目创建和任务管理
   - Git仓库自动集成
   - 标准化交付流程
   - 客户沟通模板

3. **知识库系统**
   - 自动保存可复用代码资产
   - 向量搜索和语义匹配
   - 质量评分和复用统计
   - 知识积累和反馈学习

4. **AI辅助执行**
   - 代码补全和建议
   - 自动模板生成
   - 文档自动生成
   - 质量自动检查

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/cat88666/OpenManus.git
cd OpenManus/platform
```

#### 2. 配置环境变量

```bash
# 后端配置
cp backend/.env.example backend/.env

# 编辑.env文件，填入你的API密钥
# - OPENAI_API_KEY
# - CLAUDE_API_KEY
# - UPWORK_OAUTH_TOKEN
# - LINKEDIN_EMAIL/PASSWORD
# - SMTP_USER/PASSWORD
# - TELEGRAM_BOT_TOKEN
```

#### 3. 使用Docker Compose启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

#### 4. 本地开发启动

```bash
# 后端
cd backend
pip install -r requirements.txt
python main.py

# 新终端 - Streamlit仪表板
cd streamlit-dashboard
pip install -r requirements.txt
streamlit run app.py

# 访问
# - API: http://localhost:8000
# - API文档: http://localhost:8000/docs
# - 仪表板: http://localhost:8501
```

## 📁 项目结构

```
platform/
├── backend/                    # FastAPI后端
│   ├── main.py                # 应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── models.py              # SQLAlchemy模型
│   ├── schemas.py             # Pydantic schemas
│   ├── crud.py                # 数据库操作
│   ├── llm_service.py         # LLM集成
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── streamlit-dashboard/       # Streamlit仪表板
│   ├── app.py                 # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # React前端（可选）
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
└── docker-compose.yml         # Docker编排
```

## 🔌 API文档

### 基础URL

```
http://localhost:8000/api/v1
```

### 主要端点

#### 用户管理
- `POST /users` - 创建用户
- `GET /users/{user_id}` - 获取用户
- `PUT /users/{user_id}` - 更新用户

#### 机会管理
- `POST /opportunities` - 创建机会
- `GET /opportunities/{opportunity_id}` - 获取机会
- `GET /users/{user_id}/opportunities` - 获取用户的机会列表
- `POST /opportunities/{opportunity_id}/analyze` - 分析机会
- `GET /users/{user_id}/opportunities/top` - 获取评分最高的机会

#### 申请管理
- `POST /applications` - 创建申请
- `GET /applications/{application_id}` - 获取申请
- `GET /opportunities/{opportunity_id}/applications` - 获取机会的申请列表

#### 项目管理
- `POST /projects` - 创建项目
- `GET /projects/{project_id}` - 获取项目
- `GET /users/{user_id}/projects` - 获取用户的项目列表
- `PUT /projects/{project_id}` - 更新项目

#### 任务管理
- `POST /tasks` - 创建任务
- `GET /tasks/{task_id}` - 获取任务
- `GET /projects/{project_id}/tasks` - 获取项目的任务列表

#### 知识资产
- `POST /knowledge-assets` - 创建知识资产
- `GET /knowledge-assets/{asset_id}` - 获取知识资产
- `GET /knowledge-assets` - 获取知识资产列表

#### 仪表板
- `GET /users/{user_id}/dashboard` - 获取仪表板数据

### 交互式API文档

访问 `http://localhost:8000/docs` 查看Swagger UI文档

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLite
- **ORM**: SQLAlchemy
- **向量DB**: ChromaDB
- **缓存**: Redis
- **LLM**: OpenAI + Anthropic Claude
- **异步**: AsyncIO + Celery

### 前端
- **快速原型**: Streamlit
- **生产版本**: React + TypeScript + TailwindCSS
- **可视化**: Plotly + ECharts

### 部署
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes（可选）

## 📊 数据模型

### 核心实体

```
User (用户)
  ├─ Opportunity (机会)
  │   ├─ Application (申请)
  │   └─ Project (项目)
  │       ├─ Task (任务)
  │       └─ KnowledgeAsset (知识资产)
  └─ Project (项目)
      ├─ Task (任务)
      └─ KnowledgeAsset (知识资产)

Analytics (分析数据)
```

## 🔑 关键特性

### 1. 智能机会筛选

使用LLM分析机会，评分维度：
- 预算合理性（0-20分）
- 技术栈匹配（0-25分）
- 需求明确度（0-20分）
- 客户质量（0-20分）
- 竞争程度（0-15分）

### 2. 自动申请生成

基于机会信息和历史经验，生成个性化的申请信

### 3. 知识库管理

- 自动保存项目代码和文档
- 向量搜索相似代码
- 质量评分和复用统计
- 支持多种资产类型（代码、文档、模板、工作流）

### 4. 项目管理

- 创建和跟踪项目
- 任务分解和进度管理
- Git仓库集成
- 客户沟通模板

## 📈 开发路线图

### Phase 1（Week 1-2）：接单引擎
- [x] Upwork抓取器
- [x] LLM评分系统
- [x] Web Dashboard
- [ ] 每日自动运行
- [ ] 申请跟踪系统

### Phase 2（Week 3-4）：交付管理
- [ ] 项目管理系统
- [ ] 知识库系统
- [ ] 标准化交付流程
- [ ] 客户沟通系统

### Phase 3（Week 5-6）：AI辅助
- [ ] 代码补全系统
- [ ] 模板生成
- [ ] 文档自动生成

### Phase 4（Week 7-8）：自动化执行
- [ ] 自动编码器
- [ ] 质量保证自动化
- [ ] 反馈学习系统

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

- GitHub: https://github.com/cat88666/OpenManus
- Issues: https://github.com/cat88666/OpenManus/issues

---

**最后更新**: 2026-01-13
**版本**: v1.0
