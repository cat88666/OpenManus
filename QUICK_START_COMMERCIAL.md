# 🚀 远程项目承包分包平台 - 快速启动指南

## 📋 系统概述

这是一个**完整的商业化远程项目承包分包平台**，支持：

✅ 自动爬取远程工作项目（Upwork、Toptal等）  
✅ 自动投递简历和提案  
✅ 自动接单引擎（基于利润率、技能匹配等）  
✅ 30人团队管理和分成计算  
✅ USDT支付系统  
✅ 完整的财务和数据分析  

---

## 🎯 商业模式

```
爬取项目 → 投递简历 → 获得项目 → 分配给团队 → 收取费用
                                    ↓
                            支付团队分成 (20-30%)
                                    ↓
                            平台利润 (70-80%)
```

**预期月收入**: $15,000 - $150,000  
**预期月利润**: $10,500 - $120,000

---

## 📁 项目结构

```
platform/
├── backend/
│   ├── commercial_api.py          # 完整的FastAPI接口
│   ├── commercial_crawler.py       # 爬虫和自动投递系统
│   ├── commercial_finance.py       # 团队管理和财务系统
│   └── requirements.txt            # 依赖
│
├── streamlit-dashboard/
│   ├── commercial_dashboard.py     # 完整的Streamlit仪表板
│   └── requirements.txt            # 依赖
│
└── COMMERCIAL_SYSTEM_DESIGN.md     # 详细设计文档
```

---

## 🚀 快速启动（5分钟）

### 1️⃣ 安装依赖

```bash
# 后端依赖
cd /home/ubuntu/OpenManus/platform/backend
pip install -r requirements.txt
pip install fastapi uvicorn selenium beautifulsoup4 aiohttp

# 前端依赖
cd /home/ubuntu/OpenManus/platform/streamlit-dashboard
pip install streamlit pandas plotly requests
```

### 2️⃣ 启动后端API

```bash
cd /home/ubuntu/OpenManus/platform/backend
python -m uvicorn commercial_api:app --host 0.0.0.0 --port 8000 --reload
```

访问API文档: http://localhost:8000/docs

### 3️⃣ 启动仪表板

```bash
cd /home/ubuntu/OpenManus/platform/streamlit-dashboard
streamlit run commercial_dashboard.py
```

访问仪表板: http://localhost:8501

---

## 💻 系统使用流程

### 第1步：添加团队成员

在仪表板中：
1. 点击 **"👥 团队管理"** → **"➕ 添加成员"**
2. 填写成员信息：
   - 姓名、邮箱
   - 技能（Python、Java、Go等）
   - 时薪、分成比例
   - USDT钱包地址
3. 点击 **"✅ 添加成员"**

**或使用API**:
```bash
curl -X POST http://localhost:8000/api/v1/team/members \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "skills": ["Python", "Django"],
    "hourly_rate": 50,
    "commission_rate": 0.25,
    "usdt_wallet": "wallet_address"
  }'
```

### 第2步：创建项目

在仪表板中：
1. 点击 **"📁 项目管理"** → **"➕ 创建项目"**
2. 填写项目信息：
   - 项目标题
   - 预算
   - 平台（Upwork、Toptal等）
   - 描述
3. 点击 **"✅ 创建项目"**

### 第3步：分配项目

在仪表板中：
1. 点击 **"📁 项目管理"** → **"🔗 分配项目"**
2. 选择项目和团队成员
3. 输入预估成本
4. 点击 **"✅ 分配项目"**

系统会自动：
- 计算利润
- 记录财务
- 更新成员状态

### 第4步：处理支付

在仪表板中：
1. 点击 **"💰 财务管理"** → **"💸 处理支付"**
2. 选择成员、输入支付金额
3. 确认USDT钱包地址
4. 点击 **"✅ 处理支付"**

### 第5步：查看数据

在仪表板中：
1. **"📊 仪表板"** - 查看关键指标
2. **"📈 数据分析"** - 查看详细分析
3. **"💰 财务管理"** - 查看月度统计

---

## 🤖 自动接单系统

### 启动爬虫

在仪表板中：
1. 点击 **"🤖 自动接单"**
2. 选择平台（Upwork、Toptal等）
3. 输入搜索关键词
4. 点击 **"🚀 启动爬虫"**

**或使用API**:
```bash
curl -X POST http://localhost:8000/api/v1/crawler/start \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["upwork", "toptal"],
    "keywords": ["Python", "Django", "React"]
  }'
```

### 自动接单条件

系统会自动接单，如果项目满足以下条件：

✅ 项目预算 > $500  
✅ 利润率 > 50%  
✅ 有可用团队成员  
✅ 技能匹配度 > 80%  
✅ 客户评分 > 4.0  

---

## 📊 API端点总览

### 团队管理
```
POST   /api/v1/team/members              # 创建成员
GET    /api/v1/team/members              # 获取所有成员
GET    /api/v1/team/members/{id}         # 获取单个成员
PUT    /api/v1/team/members/{id}         # 更新成员
GET    /api/v1/team/performance          # 获取绩效
POST   /api/v1/team/members/{id}/availability  # 设置可用性
```

### 项目管理
```
POST   /api/v1/projects                  # 创建项目
GET    /api/v1/projects                  # 获取所有项目
GET    /api/v1/projects/{id}             # 获取单个项目
POST   /api/v1/projects/assign           # 分配项目
```

### 财务管理
```
POST   /api/v1/finance/payment           # 处理支付
GET    /api/v1/finance/commission/{id}   # 获取分成
GET    /api/v1/finance/monthly-stats     # 获取月度统计
```

### 爬虫系统
```
POST   /api/v1/crawler/start             # 启动爬虫
```

### 自动接单
```
POST   /api/v1/auto-accept/check         # 检查是否应该接单
POST   /api/v1/auto-accept/assign        # 自动分配项目
```

### 仪表板
```
GET    /api/v1/dashboard/summary         # 获取仪表板摘要
```

---

## 💡 使用技巧

### 1. 批量添加团队成员

创建 `team_members.json`:
```json
[
  {
    "name": "Alice",
    "email": "alice@example.com",
    "skills": ["Python", "Django"],
    "hourly_rate": 50,
    "commission_rate": 0.25,
    "usdt_wallet": "wallet_alice"
  },
  {
    "name": "Bob",
    "email": "bob@example.com",
    "skills": ["React", "Vue"],
    "hourly_rate": 45,
    "commission_rate": 0.20,
    "usdt_wallet": "wallet_bob"
  }
]
```

然后运行脚本导入。

### 2. 自动化爬虫

创建 `cron` 任务自动运行爬虫：
```bash
# 每天早上8点运行
0 8 * * * curl -X POST http://localhost:8000/api/v1/crawler/start \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["upwork", "toptal"], "keywords": ["Python", "Django"]}'
```

### 3. 监控关键指标

定期检查：
- 月收入和利润
- 项目完成率
- 团队成员绩效
- 客户满意度

---

## 🔧 配置调整

### 修改自动接单条件

编辑 `commercial_finance.py`:
```python
class AutoAcceptanceEngine:
    def __init__(self):
        self.min_budget = 500           # 最小预算
        self.min_profit_margin = 0.5    # 最小利润率
        self.min_client_rating = 4.0    # 最小客户评分
```

### 修改分成比例

在添加成员时设置 `commission_rate`:
- 0.20 = 20% 分成给成员
- 0.25 = 25% 分成给成员
- 0.30 = 30% 分成给成员

---

## 📈 预期收益计算

### 保守估计（月3个项目）

| 项目 | 预算 | 成本(30%) | 利润(70%) |
|------|------|----------|----------|
| 项目1 | $5,000 | $1,500 | $3,500 |
| 项目2 | $8,000 | $2,400 | $5,600 |
| 项目3 | $10,000 | $3,000 | $7,000 |
| **总计** | **$23,000** | **$6,900** | **$16,100** |

**月利润**: $16,100  
**年利润**: $193,200

### 乐观估计（月5个项目）

**月利润**: $35,000  
**年利润**: $420,000

---

## 🆘 故障排除

### 问题1：无法连接到API

```bash
# 检查API是否运行
curl http://localhost:8000/health

# 重启API
pkill -f "uvicorn commercial_api"
python -m uvicorn commercial_api:app --host 0.0.0.0 --port 8000
```

### 问题2：仪表板无法加载

```bash
# 检查Streamlit是否运行
ps aux | grep streamlit

# 重启Streamlit
pkill -f streamlit
streamlit run commercial_dashboard.py
```

### 问题3：爬虫无法工作

- 检查网络连接
- 更新Selenium WebDriver
- 检查目标网站是否有反爬虫机制

---

## 📚 完整文档

详细的系统设计和架构说明，请查看：
- `COMMERCIAL_SYSTEM_DESIGN.md` - 系统设计文档
- `platform/backend/commercial_api.py` - API代码和注释
- `platform/streamlit-dashboard/commercial_dashboard.py` - 仪表板代码

---

## 🎯 下一步

1. ✅ 添加30人团队成员信息
2. ✅ 启动爬虫和自动投递
3. ✅ 配置自动接单条件
4. ✅ 监控第一批项目
5. ✅ 优化工作流程
6. ✅ 扩展到更多平台

---

## 📞 支持

如有问题，请查看：
- GitHub Issues: https://github.com/cat88666/OpenManus/issues
- 系统日志: 仪表板 → ⚙️ 设置 → 📝 日志

---

**准备好赚钱了吗？现在就启动系统！** 🚀

```bash
# 一键启动所有服务
cd /home/ubuntu/OpenManus
bash scripts/start_commercial.sh
```

祝您生意兴隆！💰
