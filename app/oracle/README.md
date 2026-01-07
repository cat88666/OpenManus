# Oracle - 机会感知引擎

## 简介

Oracle 是 OpenManus 的机会发现子系统，用于自动抓取、分析和推荐外包项目机会。

## 架构

```
app/oracle/
├── __init__.py           # 模块入口
├── oracle_agent.py       # Oracle智能体（整合抓取、分析、存储）
├── scrapers/             # 抓取器模块
│   ├── base_scraper.py   # 抓取器基类
│   └── upwork_scraper.py # Upwork抓取器
├── analyzer/             # 分析器模块
│   └── smart_filter.py   # LLM智能评分
├── storage/              # 存储模块
│   └── opportunity_db.py # SQLite数据库
└── dashboard/            # 可视化界面（TODO）
```

## 快速开始

### 1. 运行完整流程

```bash
# 激活环境
conda activate open_manus

# 运行Oracle
python run_oracle.py
```

### 2. 自定义参数

```bash
# 自定义关键词和预算
python run_oracle.py --keywords "react,python,fastapi" --min-budget 500 --top-n 15
```

### 3. 单独测试组件

```python
import asyncio
from app.oracle import UpworkScraper, OpportunityAnalyzer, OpportunityDB

# 测试抓取器
async def test_scraper():
    scraper = UpworkScraper()
    await scraper.initialize()
    jobs = await scraper.scrape_jobs(["react"])
    print(f"抓取到 {len(jobs)} 个职位")
    await scraper.close()

asyncio.run(test_scraper())
```

## 配置

在 `config/config.toml` 中配置LLM：

```toml
[llm]
model = "gpt-4"
api_key = "your-api-key"
```

## 数据库

数据保存在 `workspace/opportunities.db`，可以使用 SQLite 工具查看：

```bash
sqlite3 workspace/opportunities.db

# 查看Top 10
SELECT title, ai_score, budget FROM opportunities ORDER BY ai_score DESC LIMIT 10;
```

## 组件说明

### UpworkScraper

- 基于 Playwright 的 Upwork 职位抓取器
- 支持关键词搜索和过滤
- 自动提取职位标题、描述、预算、技术栈等

### OpportunityAnalyzer

- 使用 LLM 智能分析职位
- 评估维度：预算合理性、技术匹配度、需求明确度等
- 输出0-100评分和推荐建议

### OpportunityDB

- SQLite 数据库存储
- 支持按评分排序、状态过滤、关键词搜索
- 自动去重和更新

### OracleAgent

- 整合抓取、分析、存储的完整流程
- 提供每日报告功能
- 资源自动清理

## 扩展计划

- [ ] Day 2: Streamlit 可视化 Dashboard
- [ ] Day 2: 定时抓取（每小时）
- [ ] Day 3: 邮件/微信通知
- [ ] Day 3: 代理池支持
- [ ] Future: 更多平台（LinkedIn, Toptal, Freelancer）

