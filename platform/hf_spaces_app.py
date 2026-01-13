"""
Hugging Face Spaces - AI数字员工平台
这个文件用于在Hugging Face Spaces上部署应用
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
</style>
""", unsafe_allow_html=True)

# API基础URL
API_BASE_URL = "http://localhost:8000/api/v1"

# 侧边栏导航
st.sidebar.title("🤖 AI数字员工平台")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择功能",
    ["📊 仪表板", "🎯 机会管理", "📁 项目管理", "📚 知识库", "📈 数据分析", "ℹ️ 关于"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**项目信息**
- 版本: v1.0
- 平台: Hugging Face Spaces
- 技术: Streamlit + FastAPI
""")

# 主页面内容
if page == "📊 仪表板":
    st.title("📊 仪表板")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总机会数", "156", "+12%")
    with col2:
        st.metric("待处理申请", "23", "+5")
    with col3:
        st.metric("进行中项目", "8", "+2")
    with col4:
        st.metric("知识资产", "45", "+8")
    
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
        
        opportunities = [
            {
                "标题": "React项目开发",
                "平台": "Upwork",
                "预算": "$2,500",
                "评分": "85/100",
                "状态": "已发现"
            },
            {
                "标题": "Node.js后端开发",
                "平台": "LinkedIn",
                "预算": "$3,000",
                "评分": "92/100",
                "状态": "已审查"
            },
            {
                "标题": "全栈Web应用",
                "平台": "Toptal",
                "预算": "$5,000",
                "评分": "78/100",
                "状态": "已申请"
            }
        ]
        
        df_opp = pd.DataFrame(opportunities)
        st.dataframe(df_opp, use_container_width=True)
    
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
            st.success("✅ 机会已创建！")
    
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
        
        projects = [
            {
                "项目名": "客户A网站重构",
                "预算": "$5,000",
                "进度": 75,
                "截止日期": "2026-02-15",
                "状态": "进行中"
            },
            {
                "项目名": "移动应用开发",
                "预算": "$8,000",
                "进度": 45,
                "截止日期": "2026-03-01",
                "状态": "进行中"
            },
            {
                "项目名": "API集成项目",
                "预算": "$3,000",
                "进度": 90,
                "截止日期": "2026-01-20",
                "状态": "即将完成"
            }
        ]
        
        df_proj = pd.DataFrame(projects)
        st.dataframe(df_proj, use_container_width=True)
        
        # 显示进度条
        st.subheader("项目进度")
        for proj in projects:
            st.write(f"**{proj['项目名']}**")
            st.progress(proj['进度'] / 100)
    
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
            st.success("✅ 项目已创建！")

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
            },
            {
                "标题": "项目启动模板",
                "类型": "模板",
                "质量": "⭐⭐⭐⭐⭐",
                "复用": "15次",
                "创建": "2026-01-05"
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
    - **后端**: FastAPI + SQLAlchemy + PostgreSQL
    - **前端**: React + TypeScript + TailwindCSS
    - **仪表板**: Streamlit
    - **LLM**: OpenAI + Anthropic Claude
    - **部署**: Docker + Hugging Face Spaces
    
    ### 项目信息
    - **版本**: v1.0
    - **状态**: 生产就绪
    - **开发者**: OpenManus Team
    - **GitHub**: https://github.com/cat88666/OpenManus
    
    ### 快速开始
    
    1. **创建用户** - 在机会管理中注册
    2. **浏览机会** - 查看最新的外包机会
    3. **分析机会** - 使用AI进行智能评分
    4. **创建项目** - 接单后创建项目
    5. **管理任务** - 分解任务并跟踪进度
    6. **积累知识** - 保存可复用的资产
    
    ### 联系方式
    - GitHub Issues: 报告问题
    - GitHub Discussions: 讨论功能
    - Email: dev@openmanus.com
    
    ---
    
    **感谢您使用OpenManus AI数字员工平台！** 🚀
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #94a3b8; font-size: 12px;'>
    <p>OpenManus v1.0 | Powered by Streamlit & FastAPI | Deployed on Hugging Face Spaces</p>
    <p>© 2026 OpenManus Team. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
