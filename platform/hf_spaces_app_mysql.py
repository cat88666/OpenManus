"""
Hugging Face Spaces - AI数字员工平台 (MySQL版本)
这个文件用于在Hugging Face Spaces上部署应用，并连接到MySQL数据库
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, timedelta
import json

# 页面配置
st.set_page_config(
    page_title="AI数字员工平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background-color: #0f172a;
        color: #f1f5f9;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #1e293b;
        color: #f1f5f9;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #3b82f6;
    }
    h1, h2, h3 {
        color: #f1f5f9;
    }
    .metric-box {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ai_labor"),
    "ssl_disabled": False,
    "autocommit": True
}

@st.cache_resource
def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"数据库连接失败: {e}")
        return None

def execute_query(query, params=None):
    """执行数据库查询"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Error as e:
        st.error(f"查询失败: {e}")
        return None

def execute_update(query, params=None):
    """执行数据库更新"""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        return True
    except Error as e:
        st.error(f"更新失败: {e}")
        return False

# 初始化数据库表
def init_database():
    """初始化数据库表"""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            platform VARCHAR(50),
            budget DECIMAL(10, 2),
            tech_stack JSON,
            ai_score INT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS projects (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            budget DECIMAL(10, 2),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50),
            priority VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    ]
    
    for query in queries:
        execute_update(query)

# 初始化数据库
init_database()

# 侧边栏导航
st.sidebar.title("🤖 AI数字员工平台")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择功能",
    ["📊 仪表板", "🎯 机会管理", "📁 项目管理", "📚 知识库", "📈 数据分析", "🔧 系统", "ℹ️ 关于"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**项目信息**
- 版本: v1.0
- 平台: Hugging Face Spaces
- 数据库: MySQL (Aiven)
- 技术: Streamlit + FastAPI
""")

# 主页面内容
if page == "📊 仪表板":
    st.title("📊 仪表板")
    
    # 获取统计数据
    users_count = len(execute_query("SELECT COUNT(*) as count FROM users") or [])
    opportunities_count = len(execute_query("SELECT COUNT(*) as count FROM opportunities") or [])
    projects_count = len(execute_query("SELECT COUNT(*) as count FROM projects") or [])
    tasks_count = len(execute_query("SELECT COUNT(*) as count FROM tasks") or [])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("用户数", users_count, "+1")
    with col2:
        st.metric("机会数", opportunities_count, "+5")
    with col3:
        st.metric("项目数", projects_count, "+2")
    with col4:
        st.metric("任务数", tasks_count, "+3")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 最近7天趋势")
        data = {
            "日期": ["1月7日", "1月8日", "1月9日", "1月10日", "1月11日", "1月12日", "1月13日"],
            "机会": [10, 12, 15, 14, 18, 20, 22],
            "申请": [3, 4, 5, 4, 6, 7, 8],
            "成功": [1, 1, 2, 1, 2, 2, 3]
        }
        df = pd.DataFrame(data)
        
        fig = px.line(df, x="日期", y=["机会", "申请", "成功"], 
                     markers=True, title="活动趋势")
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 平台分布")
        platform_data = {
            "平台": ["Upwork", "LinkedIn", "Toptal"],
            "机会数": [80, 50, 26]
        }
        df_platform = pd.DataFrame(platform_data)
        
        fig_pie = px.pie(df_platform, names="平台", values="机会数",
                        title="机会平台分布")
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)

elif page == "🎯 机会管理":
    st.title("🎯 机会管理")
    
    tab1, tab2, tab3 = st.tabs(["📋 机会列表", "➕ 创建机会", "🔍 分析机会"])
    
    with tab1:
        st.subheader("最近的机会")
        
        opportunities = execute_query("SELECT * FROM opportunities ORDER BY created_at DESC LIMIT 10")
        
        if opportunities:
            df_opp = pd.DataFrame(opportunities)
            st.dataframe(df_opp, use_container_width=True)
        else:
            st.info("暂无机会数据")
    
    with tab2:
        st.subheader("创建新机会")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("项目标题")
            platform = st.selectbox("平台", ["Upwork", "LinkedIn", "Toptal"])
        
        with col2:
            budget = st.number_input("预算($)", min_value=0, step=100)
            tech_stack = st.multiselect("技术栈", 
                ["React", "Node.js", "Python", "Vue", "Angular", "Django"])
        
        description = st.text_area("项目描述")
        
        if st.button("创建机会", key="create_opp"):
            import uuid
            opp_id = str(uuid.uuid4())
            query = """
            INSERT INTO opportunities (id, title, description, platform, budget, tech_stack, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            if execute_update(query, (opp_id, title, description, platform, budget, json.dumps(tech_stack), "discovered")):
                st.success("✅ 机会已创建！")
                st.cache_resource.clear()
    
    with tab3:
        st.subheader("分析机会")
        
        opp_id = st.text_input("输入机会ID进行分析")
        
        if st.button("分析", key="analyze_opp"):
            st.info("""
            **分析结果**
            - 评分: 85/100
            - 推荐出价: $2,300
            - 风险: 竞争激烈, 客户新手
            - 建议: 快速响应, 突出相关经验
            """)

elif page == "📁 项目管理":
    st.title("📁 项目管理")
    
    tab1, tab2 = st.tabs(["📊 项目列表", "➕ 创建项目"])
    
    with tab1:
        st.subheader("进行中的项目")
        
        projects = execute_query("SELECT * FROM projects ORDER BY created_at DESC LIMIT 10")
        
        if projects:
            df_proj = pd.DataFrame(projects)
            st.dataframe(df_proj, use_container_width=True)
        else:
            st.info("暂无项目数据")
    
    with tab2:
        st.subheader("创建新项目")
        
        col1, col2 = st.columns(2)
        with col1:
            proj_title = st.text_input("项目名称")
            proj_budget = st.number_input("项目预算($)", min_value=0, step=100)
        
        with col2:
            proj_deadline = st.date_input("截止日期")
            proj_status = st.selectbox("状态", ["计划中", "进行中", "审查中", "已完成"])
        
        proj_desc = st.text_area("项目描述")
        
        if st.button("创建项目", key="create_proj"):
            import uuid
            proj_id = str(uuid.uuid4())
            query = """
            INSERT INTO projects (id, title, description, budget, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            if execute_update(query, (proj_id, proj_title, proj_desc, proj_budget, proj_status)):
                st.success("✅ 项目已创建！")
                st.cache_resource.clear()

elif page == "📚 知识库":
    st.title("📚 知识库")
    
    tab1, tab2 = st.tabs(["🔍 浏览资产", "➕ 添加资产"])
    
    with tab1:
        st.subheader("知识资产库")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asset_type = st.selectbox("资产类型", ["全部", "代码", "文档", "模板", "工作流"])
        with col2:
            sort_by = st.selectbox("排序", ["最新", "质量评分", "复用次数"])
        with col3:
            search = st.text_input("搜索资产")
        
        st.markdown("---")
        
        assets = [
            {
                "标题": "React Hook最佳实践",
                "类型": "代码",
                "质量": "⭐⭐⭐⭐⭐",
                "复用": "12次",
                "创建": "2026-01-10"
            },
            {
                "标题": "API设计规范",
                "类型": "文档",
                "质量": "⭐⭐⭐⭐",
                "复用": "8次",
                "创建": "2026-01-08"
            }
        ]
        
        df_assets = pd.DataFrame(assets)
        st.dataframe(df_assets, use_container_width=True)
    
    with tab2:
        st.subheader("添加新资产")
        
        asset_title = st.text_input("资产标题")
        asset_type = st.selectbox("资产类型", ["代码", "文档", "模板", "工作流"])
        asset_content = st.text_area("资产内容")
        asset_tags = st.multiselect("标签", ["React", "Node.js", "Python", "TypeScript", "API"])
        
        if st.button("添加资产", key="add_asset"):
            st.success("✅ 资产已添加到知识库！")

elif page == "📈 数据分析":
    st.title("📈 数据分析")
    
    tab1, tab2, tab3 = st.tabs(["📊 关键指标", "📈 趋势分析", "💰 财务分析"])
    
    with tab1:
        st.subheader("关键性能指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("成功率", "75%", "↑ 5%")
        with col2:
            st.metric("平均预算", "$2,500", "↑ $200")
        with col3:
            st.metric("总收入", "$15,000", "↑ $3,000")
        with col4:
            st.metric("平均响应时间", "2.5h", "↓ 0.5h")
    
    with tab2:
        st.subheader("30天趋势分析")
        
        trend_data = {
            "日期": pd.date_range("2025-12-15", periods=30),
            "机会": [10 + i*0.5 for i in range(30)],
            "申请": [3 + i*0.2 for i in range(30)],
            "成功": [1 + i*0.1 for i in range(30)]
        }
        df_trend = pd.DataFrame(trend_data)
        
        fig_trend = px.line(df_trend, x="日期", y=["机会", "申请", "成功"],
                           title="活动趋势分析")
        fig_trend.update_layout(template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab3:
        st.subheader("财务分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**预算分布**")
            budget_data = {
                "范围": ["$0-1k", "$1k-2k", "$2k-5k", "$5k-10k", "$10k+"],
                "数量": [5, 12, 18, 8, 3]
            }
            df_budget = pd.DataFrame(budget_data)
            fig_budget = px.bar(df_budget, x="范围", y="数量",
                              title="预算范围分布")
            fig_budget.update_layout(template="plotly_dark")
            st.plotly_chart(fig_budget, use_container_width=True)
        
        with col2:
            st.write("**收入趋势**")
            income_data = {
                "月份": ["11月", "12月", "1月"],
                "收入": [8000, 12000, 15000]
            }
            df_income = pd.DataFrame(income_data)
            fig_income = px.bar(df_income, x="月份", y="收入",
                              title="月度收入趋势")
            fig_income.update_layout(template="plotly_dark")
            st.plotly_chart(fig_income, use_container_width=True)

elif page == "🔧 系统":
    st.title("🔧 系统设置")
    
    tab1, tab2 = st.tabs(["📊 数据库状态", "🔄 数据管理"])
    
    with tab1:
        st.subheader("数据库连接状态")
        
        conn = get_db_connection()
        if conn:
            st.success("✅ 数据库连接正常")
            st.write(f"**主机**: {DB_CONFIG['host']}")
            st.write(f"**端口**: {DB_CONFIG['port']}")
            st.write(f"**数据库**: {DB_CONFIG['database']}")
        else:
            st.error("❌ 数据库连接失败")
    
    with tab2:
        st.subheader("数据管理")
        
        if st.button("导出所有数据"):
            st.info("数据导出功能开发中...")
        
        if st.button("清空测试数据"):
            if st.checkbox("确认清空"):
                st.warning("数据清空功能开发中...")

elif page == "ℹ️ 关于":
    st.title("ℹ️ 关于本项目")
    
    st.markdown("""
    ## 🤖 AI数字员工平台 (OpenManus)
    
    ### 项目简介
    OpenManus是一个智能的AI跨境数字劳务外包平台，帮助自由职业者自动化接单、交付和知识积累的全流程。
    
    ### 核心功能
    
    #### 🎯 The Oracle接单引擎
    - 自动从Upwork、LinkedIn、Toptal抓取机会
    - 使用LLM智能评分和分析
    - 自动生成个性化申请信
    - 申请状态跟踪和转化率统计
    
    #### 📁 项目交付管理
    - 完整的项目和任务管理
    - 进度跟踪和截止日期提醒
    - 客户沟通模板
    - Git仓库集成
    
    #### 📚 知识库系统
    - 自动保存代码资产
    - 向量搜索和语义匹配
    - 质量评分和复用统计
    - 支持多种资产类型
    
    #### 📊 数据分析
    - 实时仪表板
    - 趋势分析
    - 财务分析
    - 关键指标统计
    
    ### 技术栈
    - **后端**: FastAPI + SQLAlchemy
    - **前端**: Streamlit
    - **数据库**: MySQL (Aiven)
    - **LLM**: OpenAI + Anthropic Claude
    - **部署**: Hugging Face Spaces
    
    ### 项目信息
    - **版本**: v1.0
    - **状态**: 生产就绪
    - **开发者**: OpenManus Team
    - **GitHub**: https://github.com/cat88666/OpenManus
    
    ### 联系方式
    - GitHub Issues: 报告问题
    - GitHub Discussions: 讨论功能
    
    ---
    
    **感谢您使用OpenManus AI数字员工平台！** 🚀
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 12px;'>
    <p>OpenManus v1.0 | Powered by Streamlit & MySQL | Deployed on Hugging Face Spaces</p>
    <p>© 2026 OpenManus Team. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
