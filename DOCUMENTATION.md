# OpenManus - AI数字员工平台 完整文档

## 📋 项目概述

**OpenManus** 是一个智能AI跨境数字劳务外包平台，核心功能是自动爬取远程工作机会（Upwork、Toptal等），通过LLM智能分析，自动分配给合适的团队成员。

### 核心功能
- 🔮 **Oracle接单引擎** - 自动爬取和分析工作机会
- 🤖 **AI智能体** - 使用LLM进行智能分析和决策
- 📊 **数据可视化** - 机会分析和团队绩效展示
- 💾 **MySQL数据库** - 统一数据存储
- ⏰ **定时调度** - 每5秒自动爬取一次

---

## 🚀 快速开始

### 前置要求
- Python 3.11+
- MySQL 8.0+
- 已配置的MySQL数据库 `openmanus`

### 安装依赖
```bash
cd /home/ubuntu/OpenManus
pip install -r requirements.txt
```

### 启动定时爬虫（推荐）
```bash
# 每5秒爬取一次工作机会
python run_oracle_scheduler.py --keywords "react,python,java,go" --interval 5
```

### 单次爬取
```bash
# 执行一次爬取并显示结果
python run_oracle.py --keywords "react,python" --min-budget 300
```

---

## 📁 项目结构

```
OpenManus/
├── app/
│   ├── oracle/                    # 核心接单引擎
│   │   ├── scrapers/              # 爬虫模块
│   │   │   ├── upwork_scraper.py  # Upwork爬虫
│   │   │   ├── toptal_scraper.py  # Toptal爬虫
│   │   │   └── base_scraper.py    # 基础爬虫类
│   │   ├── analyzer/              # 分析模块
│   │   │   ├── smart_filter.py    # LLM智能分析
│   │   │   └── scoring.py         # 评分系统
│   │   ├── storage/               # 数据存储
│   │   │   └── opportunity_db.py  # MySQL数据库操作
│   │   ├── dashboard/             # 可视化界面
│   │   ├── oracle_agent.py        # Oracle智能体（核心）
│   │   └── README.md              # Oracle模块文档
│   ├── agent/                     # AI智能体框架
│   ├── jobs/                      # 工作调度系统
│   ├── tool/                      # 工具集合
│   ├── llm.py                     # LLM集成（OpenAI/Claude）
│   ├── logger.py                  # 日志系统
│   └── config.py                  # 配置管理
├── run_oracle.py                  # 单次爬取脚本
├── run_oracle_scheduler.py        # 定时爬虫脚本
├── requirements.txt               # Python依赖
├── README.md                      # 项目README
├── DOCUMENTATION.md               # 本文档
├── ai_数字员工平台.plan.md        # 项目规划
└── skills/                        # 开发指南
    ├── OpenManus 项目架构.md
    ├── OpenManus 开发指南.md
    └── Python 编码规范.md
```

---

## 🔧 核心模块说明

### 1. Oracle接单引擎 (`app/oracle/`)

**OracleAgent** 是核心类，整合了爬虫、分析、存储的完整流程。

```python
from app.oracle import OracleAgent

# 初始化
oracle = OracleAgent(
    my_skills=["React", "Python", "Java", "Go"],
    min_budget=300
)

# 发现机会
opportunities = await oracle.discover_opportunities(
    keywords=["react", "python"],
    auto_save=True  # 自动保存到MySQL
)

# 显示报告
oracle.print_daily_report(top_n=10, min_score=60)
```

### 2. 爬虫模块 (`app/oracle/scrapers/`)

支持多个平台的爬虫：
- **UpworkScraper** - Upwork职位爬虫
- **ToptalScraper** - Toptal职位爬虫
- **LinkedInScraper** - LinkedIn职位爬虫

### 3. 分析模块 (`app/oracle/analyzer/`)

使用LLM进行智能分析：
- **OpportunityAnalyzer** - 机会分析器
- **ScoringSystem** - 评分系统（0-100）

### 4. 数据存储 (`app/oracle/storage/`)

使用SQLAlchemy + MySQL：
- **OpportunityDB** - 数据库操作类
- 表结构：opportunities, teams, assignments, payments

---

## 📊 数据库架构

### MySQL数据库 `openmanus`

#### opportunities 表
```sql
CREATE TABLE opportunities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    description TEXT,
    platform VARCHAR(50),  -- upwork, toptal, linkedin
    budget DECIMAL(10, 2),
    skills JSON,           -- ["React", "Python"]
    duration VARCHAR(50),  -- short-term, long-term
    client_rating FLOAT,
    ai_score FLOAT,        -- 0-100
    status VARCHAR(20),    -- new, applied, accepted, completed
    source_url VARCHAR(500),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### teams 表
```sql
CREATE TABLE teams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    skills JSON,
    hourly_rate DECIMAL(10, 2),
    commission_rate FLOAT,  -- 0.2-0.3
    usdt_wallet VARCHAR(255),
    status VARCHAR(20),     -- available, busy, inactive
    created_at TIMESTAMP
);
```

---

## 🔄 工作流程

```
1. 定时爬虫启动 (每5秒)
   ↓
2. 爬取多个平台的工作机会
   ↓
3. 使用LLM分析机会（评分、技能匹配等）
   ↓
4. 保存到MySQL数据库
   ↓
5. 自动分配给合适的团队成员
   ↓
6. 团队成员完成工作
   ↓
7. 计算利润和分成
   ↓
8. 生成报告和统计
```

---

## 💻 API和命令

### 定时爬虫脚本
```bash
# 基础用法
python run_oracle_scheduler.py

# 自定义参数
python run_oracle_scheduler.py \
    --keywords "react,python,java,go" \
    --interval 5 \
    --min-budget 500
```

### 单次爬取脚本
```bash
python run_oracle.py \
    --keywords "react,python" \
    --min-budget 300 \
    --top-n 10 \
    --min-score 60
```

### Python API
```python
from app.oracle.storage.opportunity_db import OpportunityDB

db = OpportunityDB()

# 获取最新机会
opportunities = db.get_top_opportunities(limit=10)

# 按平台统计
stats = db.get_stats()
print(stats['by_platform'])

# 获取高评分机会
high_score = db.query_by_score(min_score=80)

# 保存机会
db.save_opportunity({
    'title': 'React开发',
    'platform': 'upwork',
    'budget': 5000,
    'skills': ['React', 'Node.js']
})
```

---

## 🛠️ 开发指南

### 添加新的爬虫源

1. 在 `app/oracle/scrapers/` 创建新爬虫类
2. 继承 `BaseScraper`
3. 实现 `scrape_jobs()` 方法

```python
from .base_scraper import BaseScraper

class MyPlatformScraper(BaseScraper):
    async def scrape_jobs(self, keywords, filters=None):
        # 实现爬虫逻辑
        jobs = []
        # ... 爬取代码 ...
        return jobs
```

### 修改分析逻辑

编辑 `app/oracle/analyzer/smart_filter.py`：
- 修改LLM提示词
- 调整评分权重
- 添加新的过滤条件

### 查询数据库

```python
from app.oracle.storage.opportunity_db import OpportunityDB

db = OpportunityDB()

# 自定义查询
from sqlalchemy import select
from app.oracle.storage.models import Opportunity

session = db.get_session()
query = select(Opportunity).where(Opportunity.budget > 5000)
results = session.execute(query).scalars().all()
```

---

## 📈 监控和调试

### 查看日志
```bash
# 实时日志
tail -f logs/openmanus.log

# 查看爬虫日志
grep "Oracle" logs/openmanus.log
```

### 数据库查询
```bash
# 连接MySQL
mysql -u avnadmin -p -h mysql-host -P 23808 openmanus

# 查看最新机会
SELECT title, budget, ai_score FROM opportunities ORDER BY created_at DESC LIMIT 10;

# 按平台统计
SELECT platform, COUNT(*) as count FROM opportunities GROUP BY platform;
```

### 性能监控
```python
from app.oracle.storage.opportunity_db import OpportunityDB

db = OpportunityDB()
stats = db.get_stats()

print(f"总机会数: {stats['total']}")
print(f"按平台: {stats['by_platform']}")
print(f"按状态: {stats['by_status']}")
```

---

## 🚨 常见问题

### Q: 爬虫无法连接到数据库
**A:** 检查MySQL连接配置：
```python
# 在 app/oracle/storage/opportunity_db.py 中修改
DATABASE_URL = "mysql://user:password@host:port/openmanus"
```

### Q: LLM分析失败
**A:** 检查OpenAI API密钥：
```bash
export OPENAI_API_KEY="your-key-here"
```

### Q: 爬虫速度慢
**A:** 调整并发数和超时时间：
```python
# 在爬虫类中修改
MAX_WORKERS = 10
TIMEOUT = 30
```

---

## 📚 相关文档

- **项目规划**: `ai_数字员工平台.plan.md`
- **项目架构**: `skills/OpenManus 项目架构.md`
- **开发指南**: `skills/OpenManus 开发指南.md`
- **编码规范**: `skills/Python 编码规范.md`
- **Oracle模块**: `app/oracle/README.md`

---

## 🔐 安全建议

1. **数据库密码** - 使用环境变量存储
2. **API密钥** - 不要提交到Git
3. **日志信息** - 不要记录敏感数据
4. **数据备份** - 定期备份MySQL数据库

---

## 📞 支持

- **GitHub Issues**: https://github.com/cat88666/OpenManus/issues
- **GitHub Discussions**: https://github.com/cat88666/OpenManus/discussions

---

**最后更新**: 2026-01-13  
**版本**: v1.0  
**状态**: 生产就绪
