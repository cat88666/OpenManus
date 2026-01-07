# AI数字员工平台实施计划 v2.0

## 重新规划核心原则

### 1. 战略调整
- **从完整系统到商业验证**: 优先验证能否接单赚钱
- **从AI自动化到人工验证**: 先用人工交付验证商业模式,再逐步自动化
- **从技术驱动到价值驱动**: 聚焦"接单-交付-收款"闭环

### 2. 重新定义优先级(基于已有环境)

**Phase 1 (Week 1-2): The Oracle - 机会捕获优先**
> **核心目标**: 每天获得3-5个高质量外包机会

**为什么Oracle优先?**
1. ✅ OpenManus环境已就绪,可直接开始抓取
2. 没有项目来源,后续无从谈起
3. 可立即验证市场需求和定价
4. 人工交付降低了对AI代码生成的依赖

**实施重点**:
- Upwork + Toptal + LinkedIn 三平台抓取
- LLM智能筛选 + 人工最终审核
- 建立机会评分系统(预算、技术栈匹配度、竞争度)
- 目标: 接到第一个付费项目

**Phase 2 (Week 3-4): 人工交付 + 知识沉淀**
- **前期100%人工交付**: 用自己的技能完成项目
- 同时建立知识库: 记录每个项目的代码、文档、流程
- 建立交付模板和最佳实践
- 目标: 完成3-5个项目,收入>$3000

**Phase 3 (Week 5-8): 渐进式AI化**
- 基于积累的知识库,开始AI辅助
- 从代码片段复用到自动化生成
- 从模板填充到智能创作
- 目标: AI辅助度达到50%,效率提升2倍

---

## 重新设计的架构

### 简化架构图(商业验证阶段)

```
┌──────────────────────────────────────┐
│     The Oracle (Week 1-2)            │
│  ┌────────────────────────────┐      │
│  │  Multi-Platform Scraper    │      │
│  │  (Upwork/Toptal/LinkedIn)  │      │
│  └──────────┬─────────────────┘      │
│             │                         │
│             ▼                         │
│  ┌────────────────────────────┐      │
│  │   LLM Smart Filter         │      │
│  │   (Budget/Tech/Competition)│      │
│  └──────────┬─────────────────┘      │
│             │                         │
│             ▼                         │
│  ┌────────────────────────────┐      │
│  │   Opportunity Dashboard    │      │
│  │   (Top 10 Daily)           │      │
│  └────────────────────────────┘      │
└──────────────┬───────────────────────┘
               │
               ▼
      ┌───────────────┐
      │ Human Review  │ ← 人工筛选3-5个申请
      │ & Bid         │
      └───────┬───────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Manual Delivery (Week 3-4)        │
│  ┌────────────────────────────┐     │
│  │  Human Coding              │     │
│  └──────────┬─────────────────┘     │
│             │                        │
│             ▼                        │
│  ┌────────────────────────────┐     │
│  │  Knowledge Base Builder    │     │
│  │  (Auto-save code/docs)     │     │
│  └──────────┬─────────────────┘     │
│             │                        │
│             ▼                        │
│  ┌────────────────────────────┐     │
│  │  Delivery & Payment        │     │
│  └────────────────────────────┘     │
└─────────────────────────────────────┘
              │
              ▼
      ┌───────────────┐
      │ Success       │ → 数据进入知识库
      │ Feedback Loop │    为AI化做准备
      └───────────────┘
```

### 数据模型简化

```python
# 核心数据模型
class JobOpportunity:
    """机会"""
    id: str
    platform: Literal["upwork", "toptal", "linkedin"]
    title: str
    description: str
    tech_stack: List[str]
    budget: float
    client_history: Dict  # 客户历史评价
    competition_level: Literal["low", "medium", "high"]
    ai_score: float  # LLM评分 0-100
    human_review: Optional[str]  # 人工备注
    status: Literal["discovered", "reviewed", "applied", "won", "rejected"]

class Project:
    """项目"""
    id: str
    opportunity: JobOpportunity
    start_date: datetime
    deadline: datetime
    deliverables: List[str]
    status: Literal["in_progress", "review", "delivered", "paid"]

class KnowledgeAsset:
    """知识资产(人工交付积累)"""
    id: str
    project_id: str
    asset_type: Literal["code", "doc", "template", "workflow"]
    content: str
    tech_tags: List[str]
    reuse_count: int = 0
    quality_score: float  # 基于项目成功度
```

---

## 8周冲刺计划(商业优先)

### Week 1-2: The Oracle - 接单引擎

**目标**: 每天获得3-5个值得申请的机会,接到第一单

**Day 1-3: 多平台抓取器**
```python
# oracle/scrapers/upwork_scraper.py
class UpworkScraper:
    """基于OpenManus BrowserUseTool"""
    async def scrape_jobs(self, keywords: List[str], filters: Dict) -> List[JobPosting]:
        """
        抓取策略:
        1. 使用API(如果可用) - 优先
        2. 浏览器自动化(BrowserUseTool) - 回退
        3. 代理轮换避免封禁
        """

# oracle/scrapers/toptal_scraper.py
class ToptalScraper:
    """Toptal通常需要账号,先做LinkedIn"""
    pass

# oracle/scrapers/linkedin_scraper.py
class LinkedInScraper:
    """LinkedIn Jobs API + 浏览器混合"""
    async def scrape_freelance_jobs(self):
        # 搜索 "freelance" "contract" 关键词
```

**实现清单**:
- [ ] Upwork抓取器(核心,必须完成)
- [ ] LinkedIn抓取器(次要,如果时间允许)
- [ ] 代理池配置(防封禁)
- [ ] 数据存储(SQLite即可)

**Day 4-7: 智能过滤和评分**
```python
# oracle/analyzer/smart_filter.py
class OpportunityAnalyzer:
    def analyze(self, job: JobPosting) -> AnalysisResult:
        """
        LLM分析维度:
        1. 预算合理性(排除过低)
        2. 技术栈匹配度(你的专长)
        3. 需求明确度(避免需求不清)
        4. 客户质量(历史评价、支付记录)
        5. 竞争程度(申请数量)

        输出: 0-100分 + 文字建议
        """
        prompt = f"""
        分析以下外包机会,给出评分(0-100):

        标题: {job.title}
        预算: {job.budget}
        技术栈: {job.tech_stack}
        客户评价: {job.client_rating}
        当前申请数: {job.proposal_count}

        我的技能: React, Python, Node.js

        评估:
        - 是否值得申请? (考虑预算/竞争/匹配度)
        - 风险点?
        - 建议出价?

        输出JSON格式.
        """
        # 调用LLM

# oracle/dashboard/opportunity_board.py
class OpportunityDashboard:
    """简单的Web界面展示Top机会"""
    def render_daily_top10(self):
        # 用FastAPI + React快速搭建
        # 或者先用Streamlit
```

**实现清单**:
- [ ] LLM分析器(基于Claude API)
- [ ] 评分系统(规则+AI混合)
- [ ] 简单Dashboard(Streamlit快速原型)
- [ ] 每日自动运行脚本

**Day 8-10: 申请和跟踪**
```python
# oracle/bidder/proposal_helper.py
class ProposalHelper:
    def generate_proposal(self, job: JobOpportunity) -> str:
        """
        LLM辅助生成申请信:
        1. 分析需求关键点
        2. 匹配个人经验
        3. 生成个性化申请
        4. 人工润色后发送
        """

# oracle/tracker/status_tracker.py
class ApplicationTracker:
    """跟踪申请状态"""
    def track(self):
        # 记录: 申请时间、回复率、转化率
```

**Week 1-2 交付物**:
- ✅ 可工作的Upwork抓取+分析系统
- ✅ 每天自动推送Top 10机会到邮箱/Telegram
- ✅ 至少申请20个项目
- ✅ **核心目标: 接到第一个付费项目($500+)**

---

### Week 3-4: 人工交付 + 知识沉淀

**目标**: 完成3-5个项目,建立可复用的知识库

**Day 11-14: 项目交付流程**
```python
# delivery/project_manager.py
class ProjectManager:
    """人工交付的项目管理"""
    def create_project(self, job: JobOpportunity):
        """
        创建项目:
        1. 建立代码仓库(Git)
        2. 创建任务清单(Notion/Trello)
        3. 设置里程碑
        """

    def track_progress(self):
        """每日进度跟踪"""

# delivery/knowledge_saver.py
class KnowledgeSaver:
    """自动保存可复用资产"""
    def on_file_save(self, file_path: str):
        """
        监听代码保存,自动分析:
        - 是组件?(React Component)
        - 是工具函数?(Utility)
        - 是配置模板?(Config)

        自动标记Tag并存入知识库
        """
```

**人工交付最佳实践**:
1. **标准化项目结构**
```
project/
├── src/              # 源代码
├── docs/             # 文档(需求、设计、API)
├── tests/            # 测试
├── deployment/       # 部署脚本
└── README.md         # 交付说明
```

2. **边做边记录**
- 代码注释要清晰(方便后续AI学习)
- 记录决策过程(为什么这样设计)
- 保存测试用例(可复用)

3. **客户沟通模板**
```python
# delivery/communication/templates.py
TEMPLATES = {
    "project_start": "Hi, I've started working on your project...",
    "milestone_update": "Completed milestone 1: ...",
    "delivery": "Project completed. Here's what I've built...",
    "request_review": "Please review the deliverables...",
}
```

**Day 15-21: 知识库建设**
```python
# knowledge/asset_manager.py
class AssetManager:
    def __init__(self):
        self.vector_db = ChromaDB()  # 语义搜索
        self.git_repo = GitRepo()    # 完整代码

    def add_asset(self, project: Project, asset: KnowledgeAsset):
        """
        保存资产:
        1. 提取代码/文档
        2. 生成embedding
        3. 关联元数据(项目、技术栈、成功度)
        """

    def search(self, query: str) -> List[Asset]:
        """搜索可复用资产"""
        # 将来AI化时,就可以从这里检索
```

**Week 3-4 交付物**:
- ✅ 完成3-5个项目(累计收入$3000+)
- ✅ 建立包含50+可复用组件的知识库
- ✅ 标准化交付流程文档
- ✅ 客户满意度>4.5/5

---

### Week 5-6: 半自动化(AI辅助)

**目标**: AI辅助度达到30%,效率提升50%

**渐进式AI化策略**:

**Level 1: 代码补全和建议(Week 5)**
```python
# ai_assistant/code_completer.py
class CodeCompleter:
    def suggest(self, current_code: str, task: str) -> List[Suggestion]:
        """
        从知识库检索相似代码:
        1. 向量搜索相似片段
        2. LLM适配当前场景
        3. 生成3个备选方案
        """
```

**Level 2: 模板自动生成(Week 5-6)**
```python
# ai_assistant/template_generator.py
class TemplateGenerator:
    def generate_boilerplate(self, project_type: str, tech_stack: List[str]):
        """
        基于历史项目生成脚手架:
        - React前端项目 → 标准目录结构
        - Python API → FastAPI模板
        - 自动配置依赖和工具
        """
```

**Level 3: 文档自动生成(Week 6)**
```python
# ai_assistant/doc_generator.py
class DocGenerator:
    def generate_readme(self, code_repo: str) -> str:
        """分析代码,自动生成README"""

    def generate_api_doc(self, api_code: str) -> str:
        """自动生成API文档"""
```

**Week 5-6 交付物**:
- ✅ AI辅助完成2-3个项目
- ✅ 开发效率提升50%(原来3天的活,现在2天完成)
- ✅ 代码复用率达到40%

---

### Week 7-8: 高度自动化(AI主导)

**目标**: AI辅助度达到70%,效率提升3倍

**核心能力: The Executor(基于积累的知识)**

```python
# executor/auto_coder.py
class AutoCoder:
    def generate_solution(self, requirement: str) -> CodeSolution:
        """
        自动生成方案:
        1. 理解需求(LLM)
        2. 拆解任务
        3. 从知识库检索最佳实践
        4. 组装代码(LLM + 模板)
        5. 自动测试
        6. 人工审核(仅关键部分)
        """

# executor/quality_checker.py
class QualityChecker:
    def auto_review(self, code: str) -> ReviewReport:
        """
        自动质量检查:
        - 静态分析(ESLint, Pylint)
        - 单元测试覆盖率
        - 安全漏洞扫描
        - LLM代码审查
        """
```

**AI化的关键: 基于真实数据训练**
```python
# training/feedback_loop.py
class FeedbackLoop:
    def learn_from_success(self, project: Project):
        """
        从成功项目学习:
        1. 提取有效模式
        2. 更新知识库权重
        3. 优化prompt模板
        """

    def learn_from_failure(self, bug_report: str):
        """
        从失败学习:
        1. 分析错误模式
        2. 更新检查规则
        3. 加强测试覆盖
        """
```

**Week 7-8 交付物**:
- ✅ AI主导完成2个中等项目
- ✅ 人工介入时间<30%
- ✅ 交付质量保持稳定(客户满意度>4.5)
- ✅ 开始并行接2-3个项目

---

## 关键技术决策

### 1. 知识库设计

**混合存储方案**:
```python
class HybridKnowledgeBase:
    def __init__(self):
        self.vector_db = ChromaDB()      # 语义搜索
        self.git_repo = GitRepo()        # 完整代码
        self.metadata_db = SQLiteDB()    # 元数据

    def add_successful_delivery(self, delivery: DeliveryTask):
        """成功交付后自动入库"""
        # 1. 提取代码片段
        # 2. 生成embedding
        # 3. 关联元数据(技术栈、使用场景、成功率)

    def retrieve(self, requirement: JobRequirement) -> List[CodeSnippet]:
        """检索相关代码"""
        # 1. 向量相似度搜索
        # 2. 根据元数据过滤(技术栈匹配)
        # 3. 按成功率排序
```

### 2. 质量保证策略

**三层质量检查**:
1. **自动化测试**(必须通过)
   - 单元测试
   - 集成测试
   - E2E测试

2. **静态分析**(警告级别)
   - 代码风格检查
   - 安全漏洞扫描
   - 性能热点分析

3. **人工审核**(前期必需)
   - 代码可读性
   - 业务逻辑正确性
   - 边界条件处理

### 3. 渐进式自动化

```
Week 1-2: 100% 人工 (建立标准)
Week 3-4: 70% 自动 + 30% 人工审核
Week 5-6: 85% 自动 + 15% 抽检
Week 7+:   95% 自动 + 5% 异常处理
```

---

## 风险缓解方案

### 风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 代码质量不稳定 | 高 | 高 | 强制人工审核+测试覆盖 |
| 抓取被封禁 | 中 | 高 | 代理池+请求限流+API回退 |
| LLM理解偏差 | 高 | 中 | 人工校验+持续训练 |
| 交付周期过长 | 中 | 中 | 限定项目范围+模板化 |
| API成本失控 | 低 | 中 | 严格预算+缓存策略 |

### 具体措施

**1. 代码质量保障**
```python
class QualityGate:
    """质量门禁"""
    def check(self, code_repo: CodeRepo) -> bool:
        checks = [
            self.test_coverage > 80,
            self.critical_bugs == 0,
            self.security_score > 90,
            self.human_review_passed
        ]
        return all(checks)
```

**2. 抓取稳定性**
```python
class ResilientScraper:
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self.rate_limiter = RateLimiter(max_requests_per_minute=10)

    async def scrape_with_retry(self, url: str, max_retries=3):
        for attempt in range(max_retries):
            try:
                await self.rate_limiter.wait()
                proxy = self.proxy_pool.get_random()
                return await self._do_scrape(url, proxy)
            except BlockedException:
                await asyncio.sleep(60 * (attempt + 1))
        raise ScrapingFailedException()
```

---

## 成功指标(商业验证优先)

### Phase 1: The Oracle (Week 1-2)
- ✅ 每天抓取 50+ 相关职位
- ✅ LLM推荐Top 10,人工审核后申请3-5个
- ✅ 申请回复率 > 20%
- ✅ **关键指标: 接到第一个付费项目($500+)**

### Phase 2: 人工交付 (Week 3-4)
- ✅ 完成3-5个项目
- ✅ 客户满意度 > 4.5/5
- ✅ 累计收入 > $3000
- ✅ 知识库积累 50+ 可复用组件
- ✅ **关键指标: 证明商业模式可行**

### Phase 3: AI辅助 (Week 5-6)
- ✅ AI辅助度 30%
- ✅ 开发效率提升 50%
- ✅ 代码复用率 40%
- ✅ 完成2-3个项目,收入 > $2000

### Phase 4: AI主导 (Week 7-8)
- ✅ AI辅助度 70%
- ✅ 开发效率提升 3倍
- ✅ 可并行处理2-3个项目
- ✅ 月收入突破 $5000
- ✅ **关键指标: 证明可规模化**

---

## 下一步行动(基于已有环境)

### 立即开始(Day 1 - 今天)

**上午(2小时): Oracle基础搭建**
```bash
# 1. 创建目录结构
cd openmanus
mkdir -p app/oracle/{scrapers,analyzer,dashboard}
mkdir -p app/knowledge
mkdir -p workspace/opportunities

# 2. 安装额外依赖
pip install chromadb beautifulsoup4 lxml

# 3. 配置文件
cp config/config.toml config/oracle_config.toml
```

**下午(4小时): 第一个Upwork抓取器**
```python
# app/oracle/scrapers/upwork_scraper.py
"""
目标: 今天就能抓到真实数据
策略: 先用最简单的方式,确保能跑通
"""

from openmanus.core.tools.browser_use_tool import BrowserUseTool

class UpworkScraper:
    def __init__(self):
        self.browser = BrowserUseTool()

    async def scrape_simple(self, keyword: str = "react"):
        """极简版本:只抓前10个职位"""
        url = f"https://www.upwork.com/nx/search/jobs/?q={keyword}"

        # 使用BrowserUseTool导航
        await self.browser.navigate(url)

        # 抓取职位列表
        jobs = await self.browser.extract_data(
            selector=".job-tile",  # Upwork的职位卡片
            fields=["title", "description", "budget"]
        )

        # 保存到本地JSON
        with open(f"workspace/opportunities/{keyword}_{date.today()}.json", "w") as f:
            json.dump(jobs, f, indent=2)

        return jobs

# 测试脚本
if __name__ == "__main__":
    scraper = UpworkScraper()
    jobs = asyncio.run(scraper.scrape_simple())
    print(f"抓取到 {len(jobs)} 个职位")
```

**晚上(2小时): 快速验证LLM分析**
```python
# app/oracle/analyzer/quick_filter.py
"""
快速验证LLM能否有效筛选
"""

class QuickFilter:
    def analyze_job(self, job: dict) -> dict:
        """用LLM快速评分"""
        prompt = f"""
        你是一个外包接单专家。评估这个项目值不值得申请:

        标题: {job['title']}
        预算: {job.get('budget', 'N/A')}
        描述: {job['description'][:500]}...

        我的技能: React, Python, FastAPI

        给出:
        1. 评分(0-100)
        2. 一句话理由
        3. 建议出价(如果值得申请)

        用JSON格式输出
        """

        # 调用Claude API
        response = call_llm(prompt)
        return json.loads(response)

# 测试
if __name__ == "__main__":
    jobs = json.load(open("workspace/opportunities/react_2026-01-07.json"))
    filter = QuickFilter()

    for job in jobs[:5]:  # 只测试前5个
        result = filter.analyze_job(job)
        print(f"[{result['score']}] {job['title']}: {result['reason']}")
```

**Day 1交付物**:
- ✅ 能抓取Upwork的脚本
- ✅ 能用LLM评分的脚本
- ✅ 看到真实数据和分析结果

---

### Day 2-3: 完善抓取和Dashboard

**Day 2上午: 增强抓取器**
- [ ] 添加错误处理和重试
- [ ] 实现代理轮换(如果需要)
- [ ] 抓取更多字段(客户评价、申请数)
- [ ] 添加日志

**Day 2下午: 数据存储**
```python
# app/oracle/storage/opportunity_db.py
"""简单的SQLite存储"""

import sqlite3
from datetime import datetime

class OpportunityDB:
    def __init__(self):
        self.conn = sqlite3.connect("workspace/opportunities.db")
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            platform TEXT,
            title TEXT,
            description TEXT,
            budget REAL,
            tech_stack TEXT,
            ai_score REAL,
            status TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """)

    def save(self, opportunity: dict):
        """保存机会"""
        self.conn.execute("""
        INSERT OR REPLACE INTO opportunities
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opportunity['id'],
            opportunity['platform'],
            # ...
        ))
        self.conn.commit()

    def get_top_opportunities(self, limit=10) -> List[dict]:
        """获取Top机会"""
        cursor = self.conn.execute("""
        SELECT * FROM opportunities
        WHERE status = 'new'
        ORDER BY ai_score DESC
        LIMIT ?
        """, (limit,))
        return cursor.fetchall()
```

**Day 3: 简单Dashboard**
```python
# app/oracle/dashboard/app.py
"""用Streamlit快速搭建Dashboard"""

import streamlit as st
from oracle.storage.opportunity_db import OpportunityDB

st.title("🎯 Daily Top Opportunities")

db = OpportunityDB()
opportunities = db.get_top_opportunities(limit=10)

for opp in opportunities:
    with st.expander(f"[{opp['ai_score']}] {opp['title']}"):
        st.write(f"**预算**: ${opp['budget']}")
        st.write(f"**技术栈**: {opp['tech_stack']}")
        st.write(opp['description'][:300] + "...")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("申请", key=opp['id']):
                st.success("已标记申请")
        with col2:
            if st.button("忽略", key=f"skip_{opp['id']}"):
                st.info("已忽略")
        with col3:
            st.link_button("查看原文", opp['url'])

# 运行: streamlit run app/oracle/dashboard/app.py
```

---

### Day 4-7: 实战申请,接第一单

**Day 4-5: 批量申请**
- 每天早上运行抓取脚本
- 审核Top 10机会
- 申请3-5个最合适的
- 用模板快速生成申请信

**申请信模板**:
```python
# oracle/templates/proposal_templates.py

TEMPLATES = {
    "react_frontend": """
Hi {client_name},

I've reviewed your requirements for {project_title} and I'm confident I can deliver a high-quality solution.

**My Relevant Experience:**
- 5+ years React development
- Built similar projects: [具体例子]
- Strong attention to detail and deadlines

**Approach:**
1. Requirement clarification (Day 1)
2. Design & architecture (Day 2-3)
3. Development & testing (Day 4-7)
4. Deployment & handover (Day 8)

**Timeline:** {estimated_days} days
**Budget:** ${proposed_budget}

I'm available to start immediately. Let's discuss your specific needs.

Best regards
""",
    # 更多模板...
}
```

**Day 6-7: 跟进和谈判**
- 及时回复客户消息
- 根据反馈调整报价
- 展示相关作品(GitHub/Portfolio)
- 目标: 接到第一个项目

**关键技巧**:
1. **快速响应**: 1小时内回复
2. **展示专业**: 详细的项目计划
3. **合理报价**: 不要太低也不要太高
4. **作品说话**: 准备2-3个demo项目

---

### Week 2: 持续抓取,同时开始交付

**每天的节奏**:
```
08:00-09:00  运行抓取脚本,审核新机会,申请2-3个
09:00-12:00  项目开发(如果已接单)
14:00-18:00  项目开发
18:00-19:00  客户沟通,进度汇报
19:00-20:00  知识沉淀(保存可复用代码)
```

**同时建立知识库**:
```python
# 每次完成一个功能,就保存下来
# knowledge/saver.py

class KnowledgeSaver:
    def save_component(self, code: str, description: str, tags: List[str]):
        """
        保存可复用组件:
        1. 代码文件
        2. 使用说明
        3. 标签和元数据
        """
        # 保存到 workspace/knowledge_base/
```

---

## 总结:从理想到现实(商业优先版)

### 原计划的问题
- ❌ 技术优先,忽视商业验证
- ❌ 过度依赖AI能力,不确定性高
- ❌ 先做交付引擎,但没有项目来源
- ❌ 没有考虑人工交付作为过渡

### 新计划的优势
- ✅ **商业优先**: Week 1-2就要接到第一单
- ✅ **人工起步**: 前期100%人工,验证商业模式
- ✅ **渐进AI化**: 基于真实数据逐步自动化
- ✅ **快速反馈**: 每个项目都积累知识资产
- ✅ **可持续**: 边赚钱边优化,降低资金压力

### 关键心态转变

**从"技术信仰"到"价值验证"**:
> "不要问AI能做什么,而要问客户需要什么"

**阶段性目标**:
1. **Week 1-2**: 证明能接到单(Oracle的价值)
2. **Week 3-4**: 证明能交付项目(人工能力验证)
3. **Week 5-6**: 证明AI能提效(自动化的价值)
4. **Week 7-8**: 证明可规模化(商业模式成立)

### 风险对冲策略

**如果Week 2还没接到单?**
→ 降低报价,扩大申请量,调整技术栈匹配

**如果Week 4交付质量不稳定?**
→ 加强人工审核,建立checklist,优化流程

**如果Week 6 AI效果不佳?**
→ 继续人工为主,AI为辅,不强求自动化

**核心原则**:
- 先活下来(接单赚钱)
- 再活得好(提高效率)
- 最后活得久(规模化)
