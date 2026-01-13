"""
Streamlit仪表板应用
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
    ["📊 仪表板", "🎯 机会", "📋 项目", "📚 知识库", "📈 分析"]
)

# 用户ID（演示用）
user_id = st.sidebar.text_input("用户ID", value="demo-user-001")

# ==================== 仪表板页面 ====================

if page == "📊 仪表板":
    st.title("📊 仪表板")
    
    try:
        # 获取仪表板数据
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/dashboard")
        if response.status_code == 200:
            data = response.json()
            
            # 显示关键指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("总机会数", data.get("total_opportunities", 0))
            
            with col2:
                st.metric("申请数", data.get("total_applications", 0))
            
            with col3:
                st.metric("项目数", data.get("total_projects", 0))
            
            with col4:
                st.metric("知识资产", data.get("knowledge_assets_count", 0))
            
            st.divider()
            
            # 最近的机会
            st.subheader("🎯 最近的机会")
            if data.get("recent_opportunities"):
                opportunities_df = pd.DataFrame(data["recent_opportunities"])
                st.dataframe(
                    opportunities_df[["title", "platform", "budget", "ai_score", "status"]],
                    use_container_width=True
                )
            else:
                st.info("暂无机会")
            
            st.divider()
            
            # 最近的项目
            st.subheader("📋 最近的项目")
            if data.get("recent_projects"):
                projects_df = pd.DataFrame(data["recent_projects"])
                st.dataframe(
                    projects_df[["title", "status", "budget", "deadline"]],
                    use_container_width=True
                )
            else:
                st.info("暂无项目")
        else:
            st.error("无法获取仪表板数据")
    except Exception as e:
        st.error(f"错误: {e}")


# ==================== 机会页面 ====================

elif page == "🎯 机会":
    st.title("🎯 机会管理")
    
    tab1, tab2, tab3 = st.tabs(["机会列表", "创建机会", "分析机会"])
    
    with tab1:
        st.subheader("机会列表")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "状态筛选",
                ["全部", "discovered", "reviewed", "applied", "won", "rejected"]
            )
        with col2:
            platform_filter = st.selectbox(
                "平台筛选",
                ["全部", "upwork", "linkedin", "toptal"]
            )
        with col3:
            limit = st.slider("显示数量", 5, 50, 10)
        
        try:
            params = {
                "skip": 0,
                "limit": limit,
                "status": None if status_filter == "全部" else status_filter,
                "platform": None if platform_filter == "全部" else platform_filter
            }
            
            response = requests.get(
                f"{API_BASE_URL}/users/{user_id}/opportunities",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    df = pd.DataFrame(data["items"])
                    st.dataframe(
                        df[["title", "platform", "budget", "ai_score", "status", "created_at"]],
                        use_container_width=True
                    )
                    
                    # 显示统计信息
                    st.info(f"总计: {data.get('total', 0)} 个机会")
                else:
                    st.info("暂无机会")
            else:
                st.error("无法获取机会列表")
        except Exception as e:
            st.error(f"错误: {e}")
    
    with tab2:
        st.subheader("创建新机会")
        
        with st.form("create_opportunity_form"):
            title = st.text_input("标题", placeholder="输入机会标题")
            description = st.text_area("描述", placeholder="输入机会描述")
            platform = st.selectbox("平台", ["upwork", "linkedin", "toptal"])
            budget = st.number_input("预算", min_value=0.0, step=100.0)
            tech_stack = st.multiselect(
                "技术栈",
                ["React", "Python", "Node.js", "FastAPI", "Vue", "Angular", "Java", "C++"]
            )
            
            if st.form_submit_button("创建"):
                try:
                    payload = {
                        "title": title,
                        "description": description,
                        "platform": platform,
                        "budget": budget,
                        "tech_stack": tech_stack
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/opportunities",
                        json=payload,
                        params={"user_id": user_id}
                    )
                    
                    if response.status_code == 200:
                        st.success("机会创建成功！")
                    else:
                        st.error("创建失败")
                except Exception as e:
                    st.error(f"错误: {e}")
    
    with tab3:
        st.subheader("分析机会")
        
        opportunity_id = st.text_input("机会ID", placeholder="输入要分析的机会ID")
        
        if st.button("分析"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/opportunities/{opportunity_id}/analyze"
                )
                
                if response.status_code == 200:
                    analysis = response.json()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("评分", f"{analysis.get('score', 0)}/100")
                    with col2:
                        st.metric("建议出价", f"${analysis.get('recommended_budget', 0)}")
                    
                    st.write("**分析理由:**")
                    st.write(analysis.get("reason", ""))
                    
                    if analysis.get("risks"):
                        st.warning("**风险点:**")
                        for risk in analysis["risks"]:
                            st.write(f"- {risk}")
                    
                    if analysis.get("recommendations"):
                        st.info("**建议:**")
                        for rec in analysis["recommendations"]:
                            st.write(f"- {rec}")
                else:
                    st.error("分析失败")
            except Exception as e:
                st.error(f"错误: {e}")


# ==================== 项目页面 ====================

elif page == "📋 项目":
    st.title("📋 项目管理")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/{user_id}/projects",
            params={"skip": 0, "limit": 20}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                df = pd.DataFrame(data["items"])
                
                # 按状态分组显示
                st.subheader("项目概览")
                
                status_counts = df["status"].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="项目状态分布"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("项目列表")
                st.dataframe(
                    df[["title", "status", "budget", "deadline", "created_at"]],
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
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/knowledge-assets",
            params={"skip": 0, "limit": 50}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                df = pd.DataFrame(data["items"])
                
                # 按资产类型分组
                st.subheader("资产类型分布")
                
                asset_type_counts = df["asset_type"].value_counts()
                fig = px.bar(
                    x=asset_type_counts.index,
                    y=asset_type_counts.values,
                    title="资产类型统计",
                    labels={"x": "资产类型", "y": "数量"}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("知识资产列表")
                st.dataframe(
                    df[["title", "asset_type", "quality_score", "reuse_count", "created_at"]],
                    use_container_width=True
                )
            else:
                st.info("暂无知识资产")
        else:
            st.error("无法获取知识资产")
    except Exception as e:
        st.error(f"错误: {e}")


# ==================== 分析页面 ====================

elif page == "📈 分析":
    st.title("📈 数据分析")
    
    st.subheader("关键指标")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("成功率", "75%", "↑ 5%")
    
    with col2:
        st.metric("平均预算", "$2,500", "↑ $200")
    
    with col3:
        st.metric("总收入", "$15,000", "↑ $3,000")
    
    st.divider()
    
    # 模拟数据
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    opportunities = [10 + i % 5 for i in range(30)]
    applications = [3 + i % 3 for i in range(30)]
    success = [1 + i % 2 for i in range(30)]
    
    df = pd.DataFrame({
        "日期": dates,
        "机会数": opportunities,
        "申请数": applications,
        "成功数": success
    })
    
    st.subheader("趋势分析")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["日期"], y=df["机会数"], name="机会数", mode="lines"))
    fig.add_trace(go.Scatter(x=df["日期"], y=df["申请数"], name="申请数", mode="lines"))
    fig.add_trace(go.Scatter(x=df["日期"], y=df["成功数"], name="成功数", mode="lines"))
    
    fig.update_layout(title="30天趋势", xaxis_title="日期", yaxis_title="数量")
    st.plotly_chart(fig, use_container_width=True)


# ==================== 页脚 ====================

st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    AI数字员工平台 v1.0 | 
    <a href='https://github.com/cat88666/OpenManus' target='_blank'>GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)
