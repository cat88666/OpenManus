# OpenManus - 完整功能架构设计

## 📋 目录
1. [系统概览](#系统概览)
2. [功能模块](#功能模块)
3. [核心流程](#核心流程)
4. [数据模型](#数据模型)
5. [API接口](#api接口)
6. [实现路线](#实现路线)

---

## 系统概览

### 项目定位
**远程项目承包和分包平台** - 自动爬取远程工作机会，分配给团队成员完成，赚取利润差价。

### 核心价值链
```
爬取机会 → 分析评分 → 自动投递 → 获得订单 → 分配团队 → 完成交付 → 计算利润 → 支付分成
```

### 用户角色
1. **平台管理员** - 您（1人）
   - 管理爬虫和投递
   - 管理团队成员
   - 管理项目和财务
   - 查看数据分析

2. **团队成员** - 30人
   - 查看分配的项目
   - 提交工作进度
   - 查看收入和分成
   - 管理个人资料

3. **客户** - 外部（Upwork等平台）
   - 发布工作机会
   - 与团队沟通
   - 验收交付物

---

## 功能模块

### 1️⃣ 机会管理模块 (Opportunity Management)

#### 功能描述
自动爬取、分析、投递远程工作机会。

#### 子功能
```
机会爬取
├── Upwork爬虫
├── Toptal爬虫
├── LinkedIn爬虫
└── 其他平台爬虫

机会分析
├── LLM智能评分
├── 技能匹配度
├── 预期收入评估
└── 风险评估

机会投递
├── 自动投递简历
├── 跟踪投递状态
├── 管理投递历史
└── 投递效果分析

机会管理
├── 机会列表展示
├── 机会详情查看
├── 机会状态更新
└── 机会归档
```

#### 数据流
```
爬虫 → 原始数据 → LLM分析 → 评分和分类 → 自动投递 → 数据库存储
```

#### 关键指标
- 每日爬取数量
- 投递成功率
- 获单率
- 平均项目价值

---

### 2️⃣ 项目管理模块 (Project Management)

#### 功能描述
管理从获单到交付的整个项目生命周期。

#### 子功能
```
项目创建
├── 手动创建项目
├── 从机会创建项目
├── 设置项目基本信息
└── 设置项目预算

项目分配
├── 选择团队成员
├── 分配任务
├── 设置截止日期
└── 设置预期收益

项目跟踪
├── 查看项目进度
├── 更新项目状态
├── 管理项目文件
└── 项目沟通记录

项目交付
├── 验收交付物
├── 确认完成
├── 记录反馈
└── 项目归档
```

#### 项目状态流转
```
新建 → 进行中 → 待验收 → 已完成 → 已归档
  ↓
  └─→ 已取消
```

#### 关键指标
- 项目总数
- 进行中项目数
- 完成率
- 平均项目周期
- 项目满意度

---

### 3️⃣ 团队管理模块 (Team Management)

#### 功能描述
管理30人团队的信息、技能、可用性和绩效。

#### 子功能
```
成员管理
├── 添加团队成员
├── 编辑成员信息
├── 删除成员
└── 批量导入

技能管理
├── 定义技能标签
├── 为成员分配技能
├── 技能等级评分
└── 技能需求分析

可用性管理
├── 设置成员可用性
├── 管理工作时间
├── 设置最大并发项目数
└── 休假管理

绩效管理
├── 项目完成率
├── 客户满意度评分
├── 交付质量评分
├── 响应时间统计
```

#### 成员信息结构
```
成员
├── 基本信息
│   ├── 姓名
│   ├── 邮箱
│   ├── 电话
│   └── 时区
├── 技能信息
│   ├── 技能列表
│   ├── 技能等级
│   └── 经验年数
├── 财务信息
│   ├── 时薪
│   ├── 分成比例（20-30%）
│   ├── USDT钱包
│   └── 银行账户
└── 状态信息
    ├── 当前状态（可用/忙碌/休假）
    ├── 当前项目数
    ├── 总完成项目数
    └── 平均评分
```

#### 关键指标
- 团队总人数
- 按技能分布
- 可用成员数
- 平均项目完成率
- 平均客户满意度

---

### 4️⃣ 财务管理模块 (Finance Management)

#### 功能描述
管理收入、成本、利润和分成。

#### 子功能
```
收入管理
├── 记录项目收入
├── 记录其他收入
├── 收入统计
└── 收入预测

成本管理
├── 记录人员成本
├── 记录运营成本
├── 成本统计
└── 成本分析

利润管理
├── 计算项目利润
├── 计算总利润
├── 利润分析
└── 利润预测

分成管理
├── 自动计算分成（20-30%）
├── 生成分成单据
├── 分成支付管理
└── 分成历史记录

支付管理
├── USDT支付处理
├── 支付记录
├── 支付对账
└── 支付报表
```

#### 财务流向
```
客户支付 → 平台收入 → 扣除成本 → 平台利润 + 成员分成
                                    ↓
                            成员USDT钱包
```

#### 关键指标
- 总收入
- 总成本
- 总利润
- 利润率（%）
- 人均收入
- 人均分成

---

### 5️⃣ 用户认证模块 (Authentication)

#### 功能描述
管理用户登录、权限控制和会话管理。

#### 子功能
```
用户认证
├── 注册
├── 登录
├── 登出
├── 密码重置
└── 邮箱验证

权限管理
├── 角色定义（管理员、成员）
├── 权限分配
├── 权限验证
└── 操作审计

会话管理
├── JWT Token生成
├── Token刷新
├── Token过期管理
└── 会话记录
```

#### 用户角色权限
```
管理员
├── 查看所有数据
├── 管理团队成员
├── 管理项目
├── 管理财务
└── 查看分析报告

成员
├── 查看分配的项目
├── 更新项目进度
├── 查看个人收入
├── 管理个人资料
└── 查看个人分析
```

---

### 6️⃣ 数据分析模块 (Analytics)

#### 功能描述
生成各类数据分析报告和可视化。

#### 子功能
```
业务分析
├── 日报告
├── 周报告
├── 月报告
├── 年报告
└── 自定义报告

财务分析
├── 收入分析
├── 成本分析
├── 利润分析
├── 分成分析
└── 现金流分析

团队分析
├── 成员绩效排名
├── 技能分布
├── 工作负载分析
├── 成员满意度
└── 离职风险预警

机会分析
├── 平台分布
├── 技能需求分析
├── 价格范围分析
├── 获单率分析
└── 投资回报率分析
```

#### 仪表板
```
主仪表板
├── KPI卡片
│   ├── 本月收入
│   ├── 本月利润
│   ├── 进行中项目数
│   └── 可用成员数
├── 趋势图表
│   ├── 收入趋势
│   ├── 项目完成趋势
│   └── 成员绩效趋势
└── 数据表格
    ├── 最新项目列表
    ├── 成员排名
    └── 机会列表
```

---

### 7️⃣ 通知系统 (Notification)

#### 功能描述
实时通知用户重要事件。

#### 子功能
```
通知类型
├── 新机会通知
├── 项目分配通知
├── 项目完成通知
├── 支付通知
├── 系统通知
└── 预警通知

通知渠道
├── 应用内通知
├── 邮件通知
├── 短信通知（可选）
└── 推送通知（可选）

通知管理
├── 通知历史
├── 通知设置
├── 通知标记已读
└── 通知删除
```

---

### 8️⃣ 集成模块 (Integration)

#### 功能描述
与外部系统和平台的集成。

#### 子功能
```
支付集成
├── USDT支付
├── Stripe集成（可选）
├── PayPal集成（可选）
└── 银行转账（可选）

平台集成
├── Upwork API
├── Toptal API
├── LinkedIn API
└── 其他平台

外部服务
├── 邮件服务
├── 短信服务
├── 云存储
└── 日志服务
```

---

## 核心流程

### 流程1: 机会获取和投递流程

```
┌─────────────────────────────────────────────────────────────┐
│                    机会获取和投递流程                         │
└─────────────────────────────────────────────────────────────┘

1. 定时爬虫启动 (每5秒)
   ↓
2. 爬取多个平台的工作机会
   ├─ Upwork爬虫
   ├─ Toptal爬虫
   ├─ LinkedIn爬虫
   └─ 其他平台
   ↓
3. 原始数据清洗和标准化
   ├─ 提取关键信息
   ├─ 验证数据完整性
   └─ 去重处理
   ↓
4. LLM智能分析
   ├─ 评分 (0-100)
   ├─ 技能匹配度
   ├─ 预期收入评估
   └─ 风险评估
   ↓
5. 保存到数据库
   ├─ 存储原始信息
   ├─ 存储分析结果
   └─ 记录爬取时间
   ↓
6. 自动投递决策
   ├─ 评分 > 70?
   ├─ 技能匹配 > 80%?
   ├─ 预期收入 > $300?
   └─ 是否已投递?
   ↓
7. 自动投递简历
   ├─ 生成个性化提案
   ├─ 提交到平台
   └─ 记录投递信息
   ↓
8. 跟踪投递状态
   ├─ 等待回复
   ├─ 获得面试
   ├─ 获得订单
   └─ 被拒绝
   ↓
9. 生成报告
   ├─ 日投递数量
   ├─ 获单率
   ├─ 平均项目价值
   └─ 成功案例分析
```

### 流程2: 项目分配和执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    项目分配和执行流程                         │
└─────────────────────────────────────────────────────────────┘

1. 获得新订单
   ├─ 客户确认合作
   ├─ 获得项目详情
   └─ 确认项目预算
   ↓
2. 创建项目
   ├─ 输入项目基本信息
   ├─ 设置项目预算
   ├─ 设置交付截止日期
   └─ 上传项目文件
   ↓
3. 分析项目需求
   ├─ 识别所需技能
   ├─ 评估项目复杂度
   ├─ 估算所需工作量
   └─ 计算预期利润
   ↓
4. 选择团队成员
   ├─ 查看可用成员
   ├─ 筛选技能匹配
   ├─ 检查工作负载
   └─ 选择最合适的成员
   ↓
5. 分配项目
   ├─ 发送项目分配通知
   ├─ 成员确认接受
   ├─ 设置项目权限
   └─ 记录分配信息
   ↓
6. 项目执行
   ├─ 成员开始工作
   ├─ 定期更新进度
   ├─ 与客户沟通
   └─ 解决遇到的问题
   ↓
7. 交付验收
   ├─ 成员提交交付物
   ├─ 管理员验收
   ├─ 客户验收
   └─ 确认无误
   ↓
8. 项目完成
   ├─ 标记为已完成
   ├─ 记录完成时间
   ├─ 记录客户反馈
   └─ 项目归档
   ↓
9. 财务结算
   ├─ 确认项目收入
   ├─ 计算成本
   ├─ 计算利润
   ├─ 计算成员分成
   └─ 生成财务单据
```

### 流程3: 财务结算和支付流程

```
┌─────────────────────────────────────────────────────────────┐
│                    财务结算和支付流程                         │
└─────────────────────────────────────────────────────────────┘

1. 项目完成
   ├─ 客户验收通过
   ├─ 确认项目收入
   └─ 记录到财务系统
   ↓
2. 成本计算
   ├─ 成员工作时间 × 时薪
   ├─ 其他项目成本
   └─ 总成本 = 工作成本 + 其他成本
   ↓
3. 利润计算
   ├─ 毛利 = 项目收入 - 成本
   ├─ 净利 = 毛利 - 运营费用
   └─ 利润率 = 净利 / 项目收入
   ↓
4. 分成计算
   ├─ 成员分成 = 成本 × (1 + 分成比例)
   ├─ 或者 = 项目收入 × 分成比例
   ├─ 平台利润 = 项目收入 - 成员分成
   └─ 记录分成单据
   ↓
5. 支付审核
   ├─ 检查分成金额
   ├─ 验证钱包地址
   ├─ 确认支付方式
   └─ 批准支付
   ↓
6. 执行支付
   ├─ 生成支付单
   ├─ 提交到支付网关
   ├─ USDT转账
   └─ 记录支付交易
   ↓
7. 支付确认
   ├─ 等待区块链确认
   ├─ 更新支付状态
   ├─ 发送支付通知
   └─ 成员查看收入
   ↓
8. 财务报表
   ├─ 生成日报表
   ├─ 生成周报表
   ├─ 生成月报表
   └─ 数据分析和预测
```

---

## 数据模型

### 核心表结构

#### 1. users 表 (用户)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'member') DEFAULT 'member',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 2. team_members 表 (团队成员)
```sql
CREATE TABLE team_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    timezone VARCHAR(50),
    skills JSON,  -- ["React", "Python", "Java"]
    skill_levels JSON,  -- {"React": "expert", "Python": "intermediate"}
    hourly_rate DECIMAL(10, 2),
    commission_rate FLOAT,  -- 0.2-0.3
    usdt_wallet VARCHAR(255),
    bank_account VARCHAR(255),
    status ENUM('available', 'busy', 'vacation', 'inactive') DEFAULT 'available',
    current_projects INT DEFAULT 0,
    max_concurrent_projects INT DEFAULT 3,
    total_completed_projects INT DEFAULT 0,
    average_rating FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 3. opportunities 表 (工作机会)
```sql
CREATE TABLE opportunities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50),  -- upwork, toptal, linkedin
    budget DECIMAL(10, 2),
    skills JSON,  -- ["React", "Node.js"]
    duration VARCHAR(50),  -- short-term, long-term
    client_rating FLOAT,
    ai_score FLOAT,  -- 0-100
    status ENUM('new', 'applied', 'accepted', 'rejected', 'completed') DEFAULT 'new',
    source_url VARCHAR(500),
    applied_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 4. projects 表 (项目)
```sql
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    opportunity_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    budget DECIMAL(10, 2),
    assigned_member_id INT,
    status ENUM('new', 'in_progress', 'pending_review', 'completed', 'archived') DEFAULT 'new',
    start_date DATE,
    end_date DATE,
    deadline DATE,
    completion_percentage INT DEFAULT 0,
    client_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
    FOREIGN KEY (assigned_member_id) REFERENCES team_members(id)
);
```

#### 5. project_tasks 表 (项目任务)
```sql
CREATE TABLE project_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    assigned_to INT,
    due_date DATE,
    estimated_hours DECIMAL(10, 2),
    actual_hours DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assigned_to) REFERENCES team_members(id)
);
```

#### 6. finances 表 (财务记录)
```sql
CREATE TABLE finances (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    member_id INT NOT NULL,
    income DECIMAL(10, 2),  -- 项目收入
    cost DECIMAL(10, 2),  -- 成本
    profit DECIMAL(10, 2),  -- 利润
    member_commission DECIMAL(10, 2),  -- 成员分成
    platform_profit DECIMAL(10, 2),  -- 平台利润
    commission_rate FLOAT,  -- 分成比例
    status ENUM('pending', 'paid', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (member_id) REFERENCES team_members(id)
);
```

#### 7. payments 表 (支付记录)
```sql
CREATE TABLE payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    finance_id INT NOT NULL,
    member_id INT NOT NULL,
    amount DECIMAL(10, 2),
    currency VARCHAR(10),  -- USDT, USD
    payment_method VARCHAR(50),  -- usdt, bank_transfer
    usdt_wallet VARCHAR(255),
    transaction_hash VARCHAR(255),
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (finance_id) REFERENCES finances(id),
    FOREIGN KEY (member_id) REFERENCES team_members(id)
);
```

#### 8. notifications 表 (通知)
```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type VARCHAR(50),  -- new_opportunity, project_assigned, payment_sent
    title VARCHAR(255),
    message TEXT,
    related_id INT,  -- opportunity_id, project_id, payment_id
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API接口

### 认证接口
```
POST   /api/v1/auth/register          - 注册
POST   /api/v1/auth/login             - 登录
POST   /api/v1/auth/logout            - 登出
POST   /api/v1/auth/refresh-token     - 刷新Token
POST   /api/v1/auth/reset-password    - 重置密码
```

### 机会管理接口
```
GET    /api/v1/opportunities          - 获取机会列表
GET    /api/v1/opportunities/:id      - 获取机会详情
POST   /api/v1/opportunities          - 创建机会
PUT    /api/v1/opportunities/:id      - 更新机会
DELETE /api/v1/opportunities/:id      - 删除机会
POST   /api/v1/opportunities/:id/apply - 投递机会
GET    /api/v1/opportunities/stats    - 获取机会统计
```

### 项目管理接口
```
GET    /api/v1/projects               - 获取项目列表
GET    /api/v1/projects/:id           - 获取项目详情
POST   /api/v1/projects               - 创建项目
PUT    /api/v1/projects/:id           - 更新项目
DELETE /api/v1/projects/:id           - 删除项目
POST   /api/v1/projects/:id/assign    - 分配项目
POST   /api/v1/projects/:id/complete  - 完成项目
GET    /api/v1/projects/stats         - 获取项目统计
```

### 团队管理接口
```
GET    /api/v1/team/members           - 获取团队成员列表
GET    /api/v1/team/members/:id       - 获取成员详情
POST   /api/v1/team/members           - 添加成员
PUT    /api/v1/team/members/:id       - 更新成员信息
DELETE /api/v1/team/members/:id       - 删除成员
GET    /api/v1/team/members/:id/performance - 获取成员绩效
GET    /api/v1/team/stats             - 获取团队统计
```

### 财务管理接口
```
GET    /api/v1/finance/records        - 获取财务记录
GET    /api/v1/finance/records/:id    - 获取财务详情
POST   /api/v1/finance/calculate      - 计算财务
GET    /api/v1/finance/stats          - 获取财务统计
POST   /api/v1/finance/export         - 导出财务报表
```

### 支付接口
```
GET    /api/v1/payments               - 获取支付列表
GET    /api/v1/payments/:id           - 获取支付详情
POST   /api/v1/payments               - 创建支付
POST   /api/v1/payments/:id/confirm   - 确认支付
GET    /api/v1/payments/stats         - 获取支付统计
```

### 分析接口
```
GET    /api/v1/analytics/dashboard    - 获取仪表板数据
GET    /api/v1/analytics/reports      - 获取报告列表
GET    /api/v1/analytics/reports/:type - 获取特定报告
GET    /api/v1/analytics/export       - 导出数据
```

### 通知接口
```
GET    /api/v1/notifications          - 获取通知列表
GET    /api/v1/notifications/:id      - 获取通知详情
POST   /api/v1/notifications/:id/read - 标记已读
DELETE /api/v1/notifications/:id      - 删除通知
```

---

## 实现路线

### 第1阶段: 核心功能 (第1周)
**目标**: 实现基础业务逻辑

- [ ] 用户认证系统
  - [ ] 用户注册/登录
  - [ ] JWT Token管理
  - [ ] 权限验证中间件

- [ ] 团队管理
  - [ ] 添加/编辑/删除成员
  - [ ] 技能管理
  - [ ] 可用性管理

- [ ] 项目管理
  - [ ] 创建/编辑/删除项目
  - [ ] 项目分配
  - [ ] 项目状态管理

- [ ] 数据库
  - [ ] 创建所有表
  - [ ] 创建索引
  - [ ] 数据库备份方案

### 第2阶段: Web界面 (第2周)
**目标**: 构建管理后台

- [ ] 后台框架搭建
  - [ ] React项目初始化
  - [ ] 路由配置
  - [ ] 状态管理

- [ ] 管理页面
  - [ ] 仪表板
  - [ ] 团队管理页面
  - [ ] 项目管理页面
  - [ ] 财务管理页面

- [ ] 数据展示
  - [ ] 表格组件
  - [ ] 图表组件
  - [ ] 导出功能

### 第3阶段: 财务和支付 (第3周)
**目标**: 完善财务系统

- [ ] 财务管理
  - [ ] 收入记录
  - [ ] 成本计算
  - [ ] 利润计算
  - [ ] 分成计算

- [ ] 支付系统
  - [ ] USDT支付集成
  - [ ] 支付记录
  - [ ] 支付对账

- [ ] 通知系统
  - [ ] 应用内通知
  - [ ] 邮件通知
  - [ ] 通知管理

### 第4阶段: 优化和部署 (第4周)
**目标**: 性能优化和上线

- [ ] 性能优化
  - [ ] 数据库查询优化
  - [ ] API缓存
  - [ ] 前端性能优化

- [ ] 测试
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] 用户验收测试

- [ ] 部署
  - [ ] 生产环境配置
  - [ ] 数据库迁移
  - [ ] 上线发布

---

## 修改指南

### 如何修改功能架构

1. **修改功能模块**
   - 编辑对应的功能描述
   - 更新子功能列表
   - 修改数据流图

2. **修改流程**
   - 编辑流程图
   - 更新流程步骤
   - 修改决策点

3. **修改数据模型**
   - 编辑表结构
   - 添加/删除字段
   - 修改字段类型

4. **修改API接口**
   - 添加/删除接口
   - 修改接口路径
   - 更新请求/响应格式

5. **修改实现路线**
   - 调整阶段划分
   - 修改任务列表
   - 更新时间估计

---

**这个文档是您的功能架构蓝图，所有后续的开发都基于这个架构。** 📋✨
