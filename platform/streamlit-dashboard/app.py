"""
Streamlit仪表板应用 - 完整版
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# 配置
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="AI数字员工平台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏导航
st.sidebar.title("🚀 AI数字员工平台")
page = st.sidebar.radio(
    "选择页面",
    ["📊 仪表板", "🎯 机会", "👥 团队", "📋 项目", "📚 知识库", "📈 分析"]
)

# ==================== 仪表板页面 ====================

if page == "📊 仪表板":
    st.title("📊 仪表板")
    
    try:
        # 获取仪表板数据
        response = requests.get(f"{API_BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            data = response.json().get("summary", {})
            
            # 显示关键指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("月度收入", f"${data.get('total_income', 0):,.0f}")
            
            with col2:
                st.metric("月度利润", f"${data.get('total_profit', 0):,.0f}")
            
            with col3:
                st.metric("团队成员", data.get('team_total', 0))
            
            with col4:
                st.metric("活跃项目", data.get('projects_active', 0))
            
            st.divider()
            
            # 显示利润率
            col1, col2 = st.columns(2)
            with col1:
                profit_margin = data.get('profit_margin', '0%')
                st.metric("利润率", profit_margin)
            
            with col2:
                completed = data.get('projects_completed', 0)
                st.metric("已完成项目", completed)
        else:
            st.error("无法获取仪表板数据")
    except Exception as e:
        st.error(f"错误: {e}")


# ==================== 机会页面 ====================

elif page == "🎯 机会":
    st.title("🎯 机会管理")
    
    tab1, tab2 = st.tabs(["机会列表", "机会分析"])
    
    with tab1:
        st.subheader("📋 机会列表")
        
        # 获取爬虫状态
        try:
            crawler_response = requests.get("http://localhost:8000/api/v1/crawler/status")
            crawler_status = crawler_response.json().get("crawler", {})
            
            # 显示爬虫状态
            col1, col2, col3 = st.columns(3)
            with col1:
                status_text = "🟢 运行中" if crawler_status.get("is_running") else "🔴 已停止"
                st.metric("爬虫状态", status_text)
            with col2:
                st.metric("爬取间隔", f"{crawler_status.get('crawl_interval', 5)}秒")
            with col3:
                st.metric("缓存机会数", crawler_status.get("cached_opportunities", 0))
            
            st.divider()
            
            # 获取最新机会
            limit = st.slider("显示数量", 5, 50, 10)
            opp_response = requests.get(
                "http://localhost:8000/api/v1/opportunities/latest",
                params={"limit": limit}
            )
            
            if opp_response.status_code == 200:
                data = opp_response.json()
                opportunities = data.get("opportunities", [])
                
                if opportunities:
                    st.success(f"✅ 共找到 {len(opportunities)} 个机会")
                    st.divider()
                    
                    # 显示机会列表
                    for idx, opp in enumerate(opportunities, 1):
                        with st.container(border=True):
                            # 第一行：来源、标题、链接
                            col1, col2, col3 = st.columns([1, 3, 1])
                            
                            with col1:
                                platform = opp.get("platform", "unknown").upper()
                                if platform == "UPWORK":
                                    st.markdown("🟢 **UPWORK**")
                                elif platform == "TOPTAL":
                                    st.markdown("🔵 **TOPTAL**")
                                elif platform == "LINKEDIN":
                                    st.markdown("⚫ **LINKEDIN**")
                                else:
                                    st.markdown(f"⚪ **{platform}**")
                            
                            with col2:
                                title = opp.get("title", "未知项目")
                                st.markdown(f"### {title}")
                            
                            with col3:
                                url = opp.get("url", "#")
                                st.markdown(f"[🔗 查看详情]({url})")
                            
                            # 第二行：描述
                            description = opp.get("description", "暂无描述")
                            st.markdown(f"**描述**: {description}")
                            
                            # 第三行：薪资、周期、评分
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                budget = opp.get("budget", 0)
                                st.markdown(f"💰 **薪资**: ${budget:,.0f}")
                            
                            with col2:
                                duration = opp.get("duration", "未知")
                                st.markdown(f"⏱️ **周期**: {duration}")
                            
                            with col3:
                                rating = opp.get("client_rating", 0)
                                st.markdown(f"⭐ **评分**: {rating}/5")
                            
                            with col4:
                                crawled_at = opp.get("crawled_at", "")
                                if crawled_at:
                                    st.markdown(f"🕐 **更新**: {crawled_at[:10]}")
                            
                            # 第四行：技能标签
                            skills = opp.get("skills", [])
                            if skills:
                                skill_tags = " ".join([f"🏷️ `{skill}`" for skill in skills])
                                st.markdown(f"**技能**: {skill_tags}")
                else:
                    st.info("暂无机会")
            else:
                st.error("无法获取机会列表")
                
        except Exception as e:
            st.error(f"错误: {e}")
    
    with tab2:
        st.subheader("机会分析")
        
        try:
            opp_response = requests.get(
                "http://localhost:8000/api/v1/opportunities/latest",
                params={"limit": 50}
            )
            
            if opp_response.status_code == 200:
                data = opp_response.json()
                opportunities = data.get("opportunities", [])
                
                if opportunities:
                    df = pd.DataFrame(opportunities)
                    
                    # 按平台统计
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        platform_counts = df["platform"].value_counts()
                        fig = px.pie(
                            values=platform_counts.values,
                            names=platform_counts.index,
                            title="平台分布"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # 薪资分布
                        fig = px.histogram(
                            df,
                            x="budget",
                            nbins=20,
                            title="薪资分布"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无数据")
        except Exception as e:
            st.error(f"错误: {e}")


# ==================== 团队页面 ====================

elif page == "👥 团队":
    st.title("👥 团队管理")
    
    tab1, tab2 = st.tabs(["团队成员", "添加成员"])
    
    with tab1:
        st.subheader("团队成员列表")
        
        try:
            response = requests.get(f"{API_BASE_URL}/team/members")
            if response.status_code == 200:
                data = response.json()
                members = data.get("members", [])
                
                if members:
                    df = pd.DataFrame(members)
                    st.dataframe(
                        df[["name", "email", "skills", "hourly_rate", "commission_rate", "availability"]],
                        use_container_width=True
                    )
                else:
                    st.info("暂无团队成员")
            else:
                st.error("无法获取团队成员")
        except Exception as e:
            st.error(f"错误: {e}")
    
    with tab2:
        st.subheader("添加新成员")
        
        with st.form("add_member_form"):
            name = st.text_input("姓名")
            email = st.text_input("邮箱")
            skills = st.multiselect(
                "技能",
                ["Python", "Java", "Go", "Node.js", "React", "Docker", "Kubernetes", "AWS"]
            )
            hourly_rate = st.number_input("时薪 ($)", min_value=10.0, step=5.0)
            commission_rate = st.slider("分成比例 (%)", 10, 50, 25)
            usdt_wallet = st.text_input("USDT钱包地址")
            
            if st.form_submit_button("添加成员"):
                try:
                    payload = {
                        "name": name,
                        "email": email,
                        "skills": skills,
                        "hourly_rate": hourly_rate,
                        "commission_rate": commission_rate / 100,
                        "usdt_wallet": usdt_wallet
                    }
                    response = requests.post(f"{API_BASE_URL}/team/members", json=payload)
                    if response.status_code == 200:
                        st.success("成员添加成功！")
                    else:
                        st.error("添加失败")
                except Exception as e:
                    st.error(f"错误: {e}")


# ==================== 项目页面 ====================

elif page == "📋 项目":
    st.title("📋 项目管理")
    
    try:
        response = requests.get(f"{API_BASE_URL}/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get("projects", [])
            
            if projects:
                df = pd.DataFrame(projects)
                st.dataframe(
                    df[["title", "status", "budget", "team_member", "deadline"]],
                    use_container_width=True
                )
            else:
                st.info("暂无项目")
        else:
            st.error("无法获取项目列表")
    except Exception as e:
        st.error(f"错误: {e}")


# ==================== 知识库页面 ====================

elif page == "📚 知识库":
    st.title("📚 知识库")
    
    st.info("知识库功能开发中...")


# ==================== 分析页面 ====================

elif page == "📈 分析":
    st.title("📈 数据分析")
    
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            data = response.json().get("summary", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("月度收入", f"${data.get('total_income', 0):,.0f}")
                st.metric("月度利润", f"${data.get('total_profit', 0):,.0f}")
            
            with col2:
                st.metric("利润率", data.get('profit_margin', '0%'))
                st.metric("项目完成率", f"{data.get('projects_completed', 0)}/{data.get('projects_total', 0)}")
    except Exception as e:
        st.error(f"错误: {e}")
