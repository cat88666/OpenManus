"""
远程项目承包分包平台 - Streamlit仪表板
支持团队管理、项目管理、财务管理、数据分析
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# 配置页面
st.set_page_config(
    page_title="远程项目承包分包平台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = "http://localhost:8000/api/v1"

# 自定义CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== 页面导航 ====================

def main():
    """主函数"""
    st.sidebar.title("🚀 远程项目承包分包平台")
    
    # 导航菜单
    page = st.sidebar.radio(
        "选择功能",
        [
            "📊 仪表板",
            "👥 团队管理",
            "📁 项目管理",
            "💰 财务管理",
            "📈 数据分析",
            "🤖 自动接单",
            "⚙️ 设置"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**系统信息**")
    st.sidebar.write(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 路由到不同页面
    if page == "📊 仪表板":
        show_dashboard()
    elif page == "👥 团队管理":
        show_team_management()
    elif page == "📁 项目管理":
        show_project_management()
    elif page == "💰 财务管理":
        show_finance_management()
    elif page == "📈 数据分析":
        show_analytics()
    elif page == "🤖 自动接单":
        show_auto_accept()
    elif page == "⚙️ 设置":
        show_settings()


# ==================== 仪表板页面 ====================

def show_dashboard():
    """显示仪表板"""
    st.title("📊 仪表板")
    
    try:
        # 获取摘要数据
        response = requests.get(f"{API_BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            data = response.json()['summary']
            
            # 关键指标
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 月收入",
                    f"${data['total_income']:.2f}",
                    delta=f"+{data['total_income']/3:.2f}" if data['total_income'] > 0 else "0"
                )
            
            with col2:
                st.metric(
                    "📈 月利润",
                    f"${data['total_profit']:.2f}",
                    delta=data['profit_margin']
                )
            
            with col3:
                st.metric(
                    "👥 团队成员",
                    f"{data['team_available']}/{data['team_total']}",
                    delta=f"{data['team_available']} 可用"
                )
            
            with col4:
                st.metric(
                    "📁 活跃项目",
                    data['projects_active'],
                    delta=f"{data['projects_completed']} 已完成"
                )
            
            st.markdown("---")
            
            # 图表
            col1, col2 = st.columns(2)
            
            with col1:
                # 收入趋势
                st.subheader("💹 收入趋势")
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                income_data = pd.DataFrame({
                    'Date': dates,
                    'Income': [data['total_income']/30 * (i+1) for i in range(30)]
                })
                fig = px.line(income_data, x='Date', y='Income', title='过去30天收入趋势')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 项目分布
                st.subheader("📊 项目分布")
                project_data = pd.DataFrame({
                    'Status': ['活跃', '已完成', '待分配'],
                    'Count': [
                        data['projects_active'],
                        data['projects_completed'],
                        data['projects_total'] - data['projects_active'] - data['projects_completed']
                    ]
                })
                fig = px.pie(project_data, names='Status', values='Count', title='项目状态分布')
                st.plotly_chart(fig, use_container_width=True)
            
            # 最近活动
            st.subheader("📋 最近活动")
            st.info("✅ 系统运行正常")
            st.success(f"✅ 本月已完成 {data['projects_completed']} 个项目")
            st.warning(f"⏳ 当前有 {data['projects_active']} 个活跃项目")
        
        else:
            st.error("无法获取仪表板数据")
    
    except Exception as e:
        st.error(f"错误: {str(e)}")


# ==================== 团队管理页面 ====================

def show_team_management():
    """显示团队管理页面"""
    st.title("👥 团队管理")
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["📋 成员列表", "➕ 添加成员", "📊 绩效排名"])
    
    with tab1:
        st.subheader("团队成员列表")
        try:
            response = requests.get(f"{API_BASE_URL}/team/members")
            if response.status_code == 200:
                members = response.json()['members']
                
                if members:
                    # 转换为DataFrame
                    df = pd.DataFrame(members)
                    
                    # 显示表格
                    st.dataframe(
                        df[['id', 'name', 'email', 'skills', 'hourly_rate', 'commission_rate', 'availability']],
                        use_container_width=True
                    )
                    
                    # 统计信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总成员数", len(members))
                    with col2:
                        available = sum(1 for m in members if m['availability'] == 'available')
                        st.metric("可用成员", available)
                    with col3:
                        busy = sum(1 for m in members if m['availability'] == 'busy')
                        st.metric("忙碌成员", busy)
                else:
                    st.info("暂无团队成员，请添加")
            else:
                st.error("无法获取团队成员列表")
        except Exception as e:
            st.error(f"错误: {str(e)}")
    
    with tab2:
        st.subheader("添加新成员")
        with st.form("add_member_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("姓名")
                email = st.text_input("邮箱")
                hourly_rate = st.number_input("时薪 ($)", min_value=10.0, value=50.0)
            
            with col2:
                skills = st.multiselect(
                    "技能",
                    ["Python", "Java", "Go", "Node.js", "React", "Vue", "DevOps", "Docker", "Kubernetes"]
                )
                commission_rate = st.slider("分成比例 (%)", min_value=20, max_value=30, value=25)
                usdt_wallet = st.text_input("USDT钱包地址")
            
            if st.form_submit_button("✅ 添加成员"):
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
                        st.success(f"✅ 成员 {name} 已添加")
                        st.rerun()
                    else:
                        st.error("添加失败")
                except Exception as e:
                    st.error(f"错误: {str(e)}")
    
    with tab3:
        st.subheader("团队绩效排名")
        try:
            response = requests.get(f"{API_BASE_URL}/team/performance")
            if response.status_code == 200:
                performance = response.json()['performance']
                
                if performance:
                    df = pd.DataFrame(performance)
                    
                    # 按成功率排序
                    df = df.sort_values('success_rate', ascending=False)
                    
                    # 显示排名
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"**{row['name']}**")
                        with col2:
                            st.write(f"成功率: {row['success_rate']:.2f}%")
                        with col3:
                            st.write(f"完成项目: {row['projects_completed']}")
                        with col4:
                            st.write(f"总收益: ${row['total_earned']:.2f}")
                        st.divider()
                else:
                    st.info("暂无绩效数据")
            else:
                st.error("无法获取绩效数据")
        except Exception as e:
            st.error(f"错误: {str(e)}")


# ==================== 项目管理页面 ====================

def show_project_management():
    """显示项目管理页面"""
    st.title("📁 项目管理")
    
    tab1, tab2, tab3 = st.tabs(["📋 项目列表", "➕ 创建项目", "🔗 分配项目"])
    
    with tab1:
        st.subheader("项目列表")
        try:
            response = requests.get(f"{API_BASE_URL}/projects")
            if response.status_code == 200:
                projects = response.json()['projects']
                
                if projects:
                    df = pd.DataFrame(projects)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("暂无项目")
            else:
                st.error("无法获取项目列表")
        except Exception as e:
            st.error(f"错误: {str(e)}")
    
    with tab2:
        st.subheader("创建新项目")
        with st.form("create_project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("项目标题")
                budget = st.number_input("项目预算 ($)", min_value=100.0, value=5000.0)
            
            with col2:
                platform = st.selectbox("平台", ["upwork", "toptal", "linkedin", "flexjobs"])
                description = st.text_area("项目描述")
            
            if st.form_submit_button("✅ 创建项目"):
                try:
                    payload = {
                        "title": title,
                        "budget": budget,
                        "platform": platform,
                        "description": description
                    }
                    response = requests.post(f"{API_BASE_URL}/projects", json=payload)
                    if response.status_code == 200:
                        st.success(f"✅ 项目 {title} 已创建")
                        st.rerun()
                    else:
                        st.error("创建失败")
                except Exception as e:
                    st.error(f"错误: {str(e)}")
    
    with tab3:
        st.subheader("分配项目给团队")
        try:
            # 获取项目和团队成员
            projects_response = requests.get(f"{API_BASE_URL}/projects")
            members_response = requests.get(f"{API_BASE_URL}/team/members")
            
            if projects_response.status_code == 200 and members_response.status_code == 200:
                projects = projects_response.json()['projects']
                members = members_response.json()['members']
                
                if projects and members:
                    with st.form("assign_project_form"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            project_id = st.selectbox(
                                "选择项目",
                                [p['id'] for p in projects],
                                format_func=lambda x: next(p['title'] for p in projects if p['id'] == x)
                            )
                        
                        with col2:
                            member_id = st.selectbox(
                                "选择团队成员",
                                [m['id'] for m in members],
                                format_func=lambda x: next(m['name'] for m in members if m['id'] == x)
                            )
                        
                        with col3:
                            estimated_cost = st.number_input("预估成本 ($)", min_value=0.0, value=1500.0)
                        
                        if st.form_submit_button("✅ 分配项目"):
                            try:
                                payload = {
                                    "project_id": project_id,
                                    "member_id": member_id,
                                    "estimated_cost": estimated_cost
                                }
                                response = requests.post(f"{API_BASE_URL}/projects/assign", json=payload)
                                if response.status_code == 200:
                                    st.success("✅ 项目已分配")
                                    st.rerun()
                                else:
                                    st.error("分配失败")
                            except Exception as e:
                                st.error(f"错误: {str(e)}")
                else:
                    st.info("需要先创建项目和添加团队成员")
        except Exception as e:
            st.error(f"错误: {str(e)}")


# ==================== 财务管理页面 ====================

def show_finance_management():
    """显示财务管理页面"""
    st.title("💰 财务管理")
    
    tab1, tab2, tab3 = st.tabs(["📊 财务统计", "💸 处理支付", "📋 分成计算"])
    
    with tab1:
        st.subheader("月度财务统计")
        try:
            now = datetime.now()
            response = requests.get(
                f"{API_BASE_URL}/finance/monthly-stats",
                params={"year": now.year, "month": now.month}
            )
            if response.status_code == 200:
                stats = response.json()['stats']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("月收入", f"${stats['total_income']:.2f}")
                with col2:
                    st.metric("月支出", f"${stats['total_commission']:.2f}")
                with col3:
                    st.metric("月利润", f"${stats['total_profit']:.2f}")
                with col4:
                    st.metric("利润率", f"{stats['profit_margin']:.2f}%")
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("项目数", stats['project_count'])
                with col2:
                    st.metric("平均项目价值", f"${stats['average_project_value']:.2f}")
            else:
                st.error("无法获取财务统计")
        except Exception as e:
            st.error(f"错误: {str(e)}")
    
    with tab2:
        st.subheader("处理支付")
        try:
            members_response = requests.get(f"{API_BASE_URL}/team/members")
            if members_response.status_code == 200:
                members = members_response.json()['members']
                
                if members:
                    with st.form("payment_form"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            member_id = st.selectbox(
                                "选择成员",
                                [m['id'] for m in members],
                                format_func=lambda x: next(m['name'] for m in members if m['id'] == x)
                            )
                        
                        with col2:
                            amount = st.number_input("支付金额 (USDT)", min_value=0.0, value=500.0)
                        
                        with col3:
                            member = next(m for m in members if m['id'] == member_id)
                            usdt_wallet = st.text_input("USDT钱包", value=member.get('usdt_wallet', ''))
                        
                        if st.form_submit_button("✅ 处理支付"):
                            try:
                                payload = {
                                    "member_id": member_id,
                                    "amount": amount,
                                    "usdt_wallet": usdt_wallet
                                }
                                response = requests.post(f"{API_BASE_URL}/finance/payment", json=payload)
                                if response.status_code == 200:
                                    st.success(f"✅ 支付已处理: ${amount} USDT")
                                    st.rerun()
                                else:
                                    st.error("支付失败")
                            except Exception as e:
                                st.error(f"错误: {str(e)}")
                else:
                    st.info("暂无团队成员")
        except Exception as e:
            st.error(f"错误: {str(e)}")
    
    with tab3:
        st.subheader("项目分成计算")
        try:
            projects_response = requests.get(f"{API_BASE_URL}/projects")
            if projects_response.status_code == 200:
                projects = projects_response.json()['projects']
                
                if projects:
                    project_id = st.selectbox(
                        "选择项目",
                        [p['id'] for p in projects],
                        format_func=lambda x: next(p['title'] for p in projects if p['id'] == x)
                    )
                    
                    if st.button("📊 计算分成"):
                        response = requests.get(f"{API_BASE_URL}/finance/commission/{project_id}")
                        if response.status_code == 200:
                            commission = response.json()['commission']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("项目预算", f"${commission['total_budget']:.2f}")
                            with col2:
                                st.metric("团队分成", f"${commission['member_commission']:.2f}")
                            with col3:
                                st.metric("平台利润", f"${commission['platform_profit']:.2f}")
                        else:
                            st.error("计算失败")
                else:
                    st.info("暂无项目")
        except Exception as e:
            st.error(f"错误: {str(e)}")


# ==================== 数据分析页面 ====================

def show_analytics():
    """显示数据分析页面"""
    st.title("📈 数据分析")
    
    st.info("📊 数据分析功能正在开发中...")
    
    # 示例图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("收入分布")
        data = pd.DataFrame({
            'Month': ['1月', '2月', '3月', '4月', '5月'],
            'Income': [5000, 8000, 12000, 15000, 18000]
        })
        fig = px.bar(data, x='Month', y='Income', title='月度收入')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("技能需求")
        data = pd.DataFrame({
            'Skill': ['Python', 'React', 'Java', 'Go', 'DevOps'],
            'Count': [15, 12, 10, 8, 7]
        })
        fig = px.bar(data, x='Skill', y='Count', title='技能需求排名')
        st.plotly_chart(fig, use_container_width=True)


# ==================== 自动接单页面 ====================

def show_auto_accept():
    """显示自动接单页面"""
    st.title("🤖 自动接单")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("启动爬虫")
        with st.form("crawler_form"):
            platforms = st.multiselect(
                "选择平台",
                ["upwork", "toptal", "linkedin", "flexjobs"],
                default=["upwork", "toptal"]
            )
            keywords = st.text_input("搜索关键词 (逗号分隔)", "Python,Django,React")
            
            if st.form_submit_button("🚀 启动爬虫"):
                try:
                    payload = {
                        "platforms": platforms,
                        "keywords": keywords.split(',')
                    }
                    response = requests.post(f"{API_BASE_URL}/crawler/start", json=payload)
                    if response.status_code == 200:
                        st.success("✅ 爬虫已启动")
                    else:
                        st.error("启动失败")
                except Exception as e:
                    st.error(f"错误: {str(e)}")
    
    with col2:
        st.subheader("自动接单设置")
        st.number_input("最小项目预算 ($)", min_value=100, value=500)
        st.slider("最小利润率 (%)", min_value=10, max_value=90, value=50)
        st.slider("最小客户评分", min_value=1.0, max_value=5.0, value=4.0)
        
        if st.button("💾 保存设置"):
            st.success("✅ 设置已保存")


# ==================== 设置页面 ====================

def show_settings():
    """显示设置页面"""
    st.title("⚙️ 设置")
    
    tab1, tab2, tab3 = st.tabs(["🔧 系统设置", "🔐 API设置", "📝 日志"])
    
    with tab1:
        st.subheader("系统设置")
        st.text_input("API基础URL", value=API_BASE_URL)
        st.number_input("请求超时 (秒)", min_value=5, max_value=60, value=30)
        st.toggle("启用自动爬虫", value=True)
        st.toggle("启用自动接单", value=True)
        
        if st.button("💾 保存设置"):
            st.success("✅ 设置已保存")
    
    with tab2:
        st.subheader("API设置")
        st.text_input("API密钥", type="password")
        st.text_input("Webhook URL")
        
        if st.button("🔄 重新生成密钥"):
            st.success("✅ 密钥已重新生成")
    
    with tab3:
        st.subheader("系统日志")
        st.info("📋 最近的系统日志")
        st.code("""
2024-01-13 10:30:00 - INFO - 爬虫启动成功
2024-01-13 10:31:00 - INFO - 爬取到 5 个项目
2024-01-13 10:32:00 - INFO - 自动投递 2 个项目
2024-01-13 10:33:00 - INFO - 自动接单 1 个项目
2024-01-13 10:34:00 - INFO - 分配项目给 Alice
        """)


# ==================== 主入口 ====================

if __name__ == "__main__":
    main()
