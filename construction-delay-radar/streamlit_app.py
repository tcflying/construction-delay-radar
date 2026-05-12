"""
Construction Delay Radar AI - Streamlit Frontend
建筑工程进度延迟风险预测系统 - MVP前端
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import sys
import os

# Configuration
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")
API_PREFIX = "/api"

# Page config
st.set_page_config(
    page_title="Construction Delay Radar AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Risk level colors
RISK_COLORS = {
    "LOW": "green",
    "MEDIUM": "yellow",
    "HIGH": "orange",
    "CRITICAL": "red"
}


def get_api_url(endpoint: str) -> str:
    """Build full API URL"""
    return f"{API_BASE_URL}{API_PREFIX}{endpoint}"


def check_health() -> dict:
    """Check API health"""
    try:
        response = requests.get(get_api_url("/health"), timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def create_project(name: str, location: str, start_date: date,
                   duration_days: int, description: str = None) -> dict:
    """Create a new project"""
    payload = {
        "name": name,
        "location": location,
        "start_date": start_date.isoformat(),
        "duration_days": duration_days,
        "description": description
    }
    response = requests.post(get_api_url("/projects/"), json=payload, timeout=10)
    return {"status": response.status_code, "data": response.json() if response.status_code in [200, 201] else response.text}


def predict_delay(project_id: str, progress_percent: int,
                 weather_delays_days: float, resource_shortage_score: float,
                 supply_chain_score: float, historical_performance: float) -> dict:
    """Get delay prediction for a project"""
    payload = {
        "project_id": project_id,
        "progress_percent": progress_percent,
        "weather_delays_days": weather_delays_days,
        "resource_shortage_score": resource_shortage_score,
        "supply_chain_score": supply_chain_score,
        "historical_performance": historical_performance
    }
    response = requests.post(get_api_url("/predict/"), json=payload, timeout=10)
    return {"status": response.status_code, "data": response.json() if response.status_code == 200 else response.text}


def get_model_info() -> dict:
    """Get ML model info"""
    try:
        response = requests.get(get_api_url("/model/info"), timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


# Initialize session state
if "projects" not in st.session_state:
    st.session_state.projects = []
if "predictions" not in st.session_state:
    st.session_state.predictions = {}
if "current_project" not in st.session_state:
    st.session_state.current_project = None


# Header
st.title("🏗️ Construction Delay Radar AI")
st.markdown("*建筑工程进度延迟风险预测系统*")

# Sidebar - Navigation
st.sidebar.title("导航")
page = st.sidebar.radio("选择功能", ["📊 仪表盘", "➕ 新建项目", "🔮 延迟预测", "ℹ️ 系统信息"])

# API Status in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("API状态")
health = check_health()
if health:
    st.sidebar.success(f"✅ 在线 (v{health.get('version', '?')})")
else:
    st.sidebar.error("❌ 离线 - 请启动API服务")

# Main content
if page == "📊 仪表盘":
    st.header("项目仪表盘")

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总项目数", len(st.session_state.projects))
    with col2:
        high_risk = sum(1 for p in st.session_state.projects if p.get("risk_level") == "HIGH")
        st.metric("高风险项目", high_risk)
    with col3:
        medium_risk = sum(1 for p in st.session_state.projects if p.get("risk_level") == "MEDIUM")
        st.metric("中风险项目", medium_risk)
    with col4:
        low_risk = sum(1 for p in st.session_state.projects if p.get("risk_level") == "LOW")
        st.metric("低风险项目", low_risk)

    st.markdown("---")

    # Projects table
    if st.session_state.projects:
        df = pd.DataFrame(st.session_state.projects)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无项目。请先创建项目或进行预测。")

    # Quick prediction section
    st.subheader("快速风险评估")
    with st.expander("输入项目特征进行快速评估"):
        col1, col2 = st.columns(2)
        with col1:
            progress = st.slider("进度百分比", 0, 100, 50)
            weather = st.number_input("天气延误(天)", 0.0, 30.0, 5.0, 0.5)
        with col2:
            resource = st.slider("资源短缺评分", 0.0, 1.0, 0.3, 0.1)
            supply_chain = st.slider("供应链评分", 0.0, 1.0, 0.4, 0.1)

        historical = st.slider("历史绩效", 0.0, 1.0, 0.75, 0.05)

        if st.button("🔮 获取快速预测", type="primary"):
            result = predict_delay(
                project_id="QUICK-001",
                progress_percent=progress,
                weather_delays_days=weather,
                resource_shortage_score=resource,
                supply_chain_score=supply_chain,
                historical_performance=historical
            )
            if result["status"] == 200:
                data = result["data"]
                st.success(f"预测延迟: {data['predicted_delay_days']} 天 | 风险等级: {data['risk_level']}")
            else:
                st.error(f"预测失败: {result['data']}")


elif page == "➕ 新建项目":
    st.header("创建新项目")

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("项目名称 *", placeholder="例如: Brooklyn中学翻新工程")
            location = st.text_input("项目位置 *", placeholder="例如: Brooklyn, NYC")
            start_date = st.date_input("计划开始日期 *", date.today())
        with col2:
            duration = st.number_input("计划工期(天) *", 30, 3650, 365, 30)
            description = st.text_area("项目描述", placeholder="可选 - 项目详细描述")

        submitted = st.form_submit_button("创建项目", type="primary")

        if submitted and name and location:
            result = create_project(name, location, start_date, duration, description)
            if result["status"] in [200, 201]:
                st.success("项目创建成功!")
                st.session_state.projects.append(result["data"])
            else:
                st.error(f"创建失败: {result['data']}")


elif page == "🔮 延迟预测":
    st.header("延迟风险预测")

    # Project selection
    if st.session_state.projects:
        project_names = [p.get("id", "Unknown") + " - " + p.get("name", "") for p in st.session_state.projects]
        selected = st.selectbox("选择项目", project_names)
        project_id = selected.split(" - ")[0] if " - " in selected else selected
    else:
        st.warning("暂无项目。请先创建项目。")
        project_id = None

    st.markdown("---")

    # Prediction inputs
    st.subheader("输入预测参数")

    col1, col2, col3 = st.columns(3)
    with col1:
        progress = st.slider("当前进度 (%)", 0, 100, 35,
                            help="项目当前完成百分比")
        weather_delays = st.number_input("天气延误 (天)", 0.0, 90.0, 5.0, 0.5,
                                        help="因天气导致的延误天数")
    with col2:
        resource_shortage = st.slider("资源短缺评分", 0.0, 1.0, 0.5, 0.1,
                                    help="0=充足, 1=严重短缺")
        supply_chain = st.slider("供应链评分", 0.0, 1.0, 0.4, 0.1,
                                help="0=顺畅, 1=严重中断")
    with col3:
        historical_perf = st.slider("历史绩效", 0.0, 1.0, 0.75, 0.05,
                                   help="承包商历史绩效 (0-1)")

    if st.button("🔮 开始预测", type="primary", disabled=project_id is None):
        result = predict_delay(
            project_id=project_id,
            progress_percent=progress,
            weather_delays_days=weather_delays,
            resource_shortage_score=resource_shortage,
            supply_chain_score=supply_chain,
            historical_performance=historical_perf
        )

        if result["status"] == 200:
            data = result["data"]

            # Store prediction
            st.session_state.predictions[project_id] = data

            # Display results
            st.success("预测完成!")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("预测延迟天数", f"{data['predicted_delay_days']} 天")
            with col2:
                risk_color = RISK_COLORS.get(data['risk_level'], "gray")
                st.markdown(f"风险等级: :{risk_color}[**{data['risk_level']}**]")
            with col3:
                st.metric("置信度", f"{data['confidence']*100:.0f}%")

            # Risk factors
            st.subheader("关键风险因素")
            factors_df = pd.DataFrame(data['factors'])
            if not factors_df.empty:
                factors_df.columns = ['因素', '影响']
                st.dataframe(factors_df, use_container_width=True)

            # Recommendations
            st.subheader("建议措施")
            for i, rec in enumerate(data['recommendations'], 1):
                st.write(f"{i}. {rec}")
        else:
            st.error(f"预测失败: {result['data']}")


elif page == "ℹ️ 系统信息":
    st.header("系统信息")

    # Model info
    model_info = get_model_info()
    if model_info:
        st.json(model_info)
    else:
        st.warning("无法获取模型信息 - API可能离线")

    st.markdown("---")

    # API endpoints
    st.subheader("API端点")
    endpoints = [
        ("GET", "/api/health", "健康检查"),
        ("POST", "/api/projects/", "创建项目"),
        ("GET", "/api/projects/", "获取项目列表"),
        ("POST", "/api/predict/", "延迟预测"),
        ("GET", "/api/model/info", "模型信息")
    ]

    for method, path, desc in endpoints:
        col1, col2, col3 = st.columns([1, 3, 4])
        with col1:
            color = "green" if method == "GET" else "blue"
            st.markdown(f":{color}[{method}]")
        with col2:
            st.code(path)
        with col3:
            st.write(desc)

    st.markdown("---")
    st.caption("Construction Delay Radar AI v0.1.0 - MVP")


if __name__ == "__main__":
    # For local development
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__,
                    "--server.port", "8501", "--server.address", "0.0.0.0"])
