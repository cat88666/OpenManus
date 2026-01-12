# API文档

## 基础信息

**基础URL**: `http://localhost:8000/api/v1`

**认证**: 目前为演示版本，暂不需要认证。生产环境应使用JWT或OAuth2。

**响应格式**: JSON

**字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "id": "xxx",
  "data": {...},
  "timestamp": "2026-01-13T10:00:00Z"
}
```

### 错误响应
```json
{
  "detail": "错误信息",
  "status_code": 400
}
```

## 端点列表

### 1. 用户管理

#### 创建用户
```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

**响应**:
```json
{
  "id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取用户
```http
GET /users/{user_id}
```

#### 更新用户
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "username": "john_doe_updated",
  "email": "john.new@example.com"
}
```

### 2. 机会管理

#### 创建机会
```http
POST /opportunities?user_id={user_id}
Content-Type: application/json

{
  "title": "React项目开发",
  "description": "需要开发一个React应用...",
  "platform": "upwork",
  "budget": 2500,
  "tech_stack": ["React", "Node.js", "MongoDB"],
  "client_rating": 4.8,
  "proposal_count": 15
}
```

**响应**:
```json
{
  "id": "opp_123",
  "title": "React项目开发",
  "platform": "upwork",
  "budget": 2500,
  "status": "discovered",
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取机会
```http
GET /opportunities/{opportunity_id}
```

#### 列出用户的机会
```http
GET /users/{user_id}/opportunities?skip=0&limit=10&status=discovered&platform=upwork
```

**查询参数**:
- `skip`: 跳过的记录数（默认0）
- `limit`: 返回的最大记录数（默认10）
- `status`: 筛选状态（discovered, reviewed, applied, won, rejected）
- `platform`: 筛选平台（upwork, linkedin, toptal）

**响应**:
```json
{
  "total": 50,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": "opp_123",
      "title": "React项目开发",
      "platform": "upwork",
      "budget": 2500,
      "status": "discovered"
    }
  ]
}
```

#### 分析机会
```http
POST /opportunities/{opportunity_id}/analyze
```

**响应**:
```json
{
  "score": 85,
  "reason": "预算合理，技术栈匹配度高...",
  "recommended_budget": 2300,
  "risks": ["竞争激烈", "客户新手"],
  "recommendations": ["快速响应", "突出相关经验"]
}
```

#### 获取评分最高的机会
```http
GET /users/{user_id}/opportunities/top?limit=10
```

### 3. 申请管理

#### 创建申请
```http
POST /applications
Content-Type: application/json

{
  "opportunity_id": "opp_123",
  "proposal_text": "我对这个项目很感兴趣...",
  "proposed_budget": 2300
}
```

**响应**:
```json
{
  "id": "app_123",
  "opportunity_id": "opp_123",
  "proposal_text": "我对这个项目很感兴趣...",
  "proposed_budget": 2300,
  "status": "sent",
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取申请
```http
GET /applications/{application_id}
```

#### 列出机会的申请
```http
GET /opportunities/{opportunity_id}/applications?skip=0&limit=10
```

### 4. 项目管理

#### 创建项目
```http
POST /projects?user_id={user_id}
Content-Type: application/json

{
  "title": "客户项目A",
  "description": "为客户A开发的项目...",
  "budget": 5000,
  "opportunity_id": "opp_123"
}
```

**响应**:
```json
{
  "id": "proj_123",
  "title": "客户项目A",
  "budget": 5000,
  "status": "in_progress",
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取项目
```http
GET /projects/{project_id}
```

#### 列出用户的项目
```http
GET /users/{user_id}/projects?skip=0&limit=10&status=in_progress
```

#### 更新项目
```http
PUT /projects/{project_id}
Content-Type: application/json

{
  "status": "review",
  "completion_percentage": 90
}
```

### 5. 任务管理

#### 创建任务
```http
POST /tasks
Content-Type: application/json

{
  "project_id": "proj_123",
  "title": "实现登录功能",
  "description": "使用JWT实现用户登录...",
  "priority": "high",
  "due_date": "2026-02-13T23:59:59Z"
}
```

**响应**:
```json
{
  "id": "task_123",
  "project_id": "proj_123",
  "title": "实现登录功能",
  "status": "todo",
  "priority": "high",
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取任务
```http
GET /tasks/{task_id}
```

#### 列出项目的任务
```http
GET /projects/{project_id}/tasks?skip=0&limit=20
```

### 6. 知识资产

#### 创建知识资产
```http
POST /knowledge-assets
Content-Type: application/json

{
  "title": "React Hook最佳实践",
  "content": "const useCustomHook = () => { ... }",
  "asset_type": "code",
  "language": "javascript",
  "tech_tags": ["React", "Hooks"],
  "project_id": "proj_123"
}
```

**响应**:
```json
{
  "id": "asset_123",
  "title": "React Hook最佳实践",
  "asset_type": "code",
  "quality_score": 0.5,
  "reuse_count": 0,
  "created_at": "2026-01-13T10:00:00Z"
}
```

#### 获取知识资产
```http
GET /knowledge-assets/{asset_id}
```

#### 列出知识资产
```http
GET /knowledge-assets?asset_type=code&skip=0&limit=50
```

### 7. 仪表板

#### 获取仪表板数据
```http
GET /users/{user_id}/dashboard
```

**响应**:
```json
{
  "total_opportunities": 50,
  "total_applications": 15,
  "total_projects": 5,
  "knowledge_assets_count": 20,
  "recent_opportunities": [...],
  "recent_projects": [...]
}
```

## 错误代码

| 代码 | 说明 |
|------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器错误 |

## 数据类型

### 用户对象
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 机会对象
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "platform": "string",
  "budget": "number",
  "tech_stack": ["string"],
  "client_rating": "number",
  "proposal_count": "number",
  "ai_score": "number",
  "status": "string",
  "created_at": "datetime"
}
```

### 申请对象
```json
{
  "id": "string",
  "opportunity_id": "string",
  "proposal_text": "string",
  "proposed_budget": "number",
  "status": "string",
  "created_at": "datetime"
}
```

### 项目对象
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "budget": "number",
  "status": "string",
  "deadline": "datetime",
  "created_at": "datetime"
}
```

### 任务对象
```json
{
  "id": "string",
  "project_id": "string",
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "due_date": "datetime",
  "created_at": "datetime"
}
```

## 使用示例

### Python
```python
import requests

# 创建用户
response = requests.post(
    'http://localhost:8000/api/v1/users',
    json={
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'secure_password'
    }
)
user = response.json()
user_id = user['id']

# 创建机会
response = requests.post(
    f'http://localhost:8000/api/v1/opportunities?user_id={user_id}',
    json={
        'title': 'React项目',
        'description': '需要开发React应用',
        'platform': 'upwork',
        'budget': 2500,
        'tech_stack': ['React', 'Node.js']
    }
)
opportunity = response.json()

# 分析机会
response = requests.post(
    f'http://localhost:8000/api/v1/opportunities/{opportunity["id"]}/analyze'
)
analysis = response.json()
print(f"评分: {analysis['score']}")
```

### JavaScript
```javascript
// 创建用户
const response = await fetch('http://localhost:8000/api/v1/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'secure_password'
  })
});
const user = await response.json();

// 获取机会列表
const opportunitiesResponse = await fetch(
  `http://localhost:8000/api/v1/users/${user.id}/opportunities?limit=10`
);
const opportunities = await opportunitiesResponse.json();
```

### cURL
```bash
# 创建用户
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password"
  }'

# 获取机会列表
curl http://localhost:8000/api/v1/users/user_123/opportunities?limit=10
```

## 速率限制

目前暂无速率限制。生产环境应根据需要实施。

## 版本管理

当前API版本: v1

未来版本将通过URL路径区分: `/api/v2`, `/api/v3` 等

---

**最后更新**: 2026-01-13
**版本**: v1.0
