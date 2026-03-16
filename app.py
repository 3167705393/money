"""资金追踪系统 - 主页仪表盘"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_manager import (
    get_all_records, get_platforms, get_channel_types,
    get_total_amount, get_platform_stats, get_channel_stats,
    get_recent_history, get_platform_name, get_channel_name
)

st.set_page_config(
    page_title="资金追踪",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 样式
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main .block-container {padding-top: 2rem;}

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 1.5rem; color: white;
        text-align: center; margin-bottom: 1rem;
    }
    .stat-value {font-size: 2rem; font-weight: 700;}
    .stat-label {font-size: 0.9rem; opacity: 0.9;}

    .page-header {
        text-align: center; padding: 1.5rem 0 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -2rem -2rem 1.5rem -2rem; border-radius: 0 0 20px 20px;
    }
    .page-header h1 {color: white; font-size: 2rem; margin: 0;}
    .page-header p {color: rgba(255,255,255,0.9); margin-top: 0.3rem;}

    .history-item {
        background: #f8f9ff; border-radius: 10px; padding: 1rem;
        margin-bottom: 0.5rem; border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)


def render_stats_cards():
    """渲染统计卡片"""
    records = get_all_records()
    platforms = get_platforms()
    total = get_total_amount()
    platform_count = len(set(r["platform_id"] for r in records))
    account_count = len(records)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="stat-value">¥{total:,.2f}</div>
            <div class="stat-label">总资产</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-value">{platform_count}</div>
            <div class="stat-label">平台数</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="stat-value">{account_count}</div>
            <div class="stat-label">账户数</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # 计算今日变动
        history = get_recent_history(20)
        today = __import__('datetime').datetime.now().strftime("%Y-%m-%d")
        today_change = sum(h["change"] for h in history if h["changed_at"].startswith(today))
        color = "#4ade80" if today_change >= 0 else "#f87171"
        sign = "+" if today_change >= 0 else ""
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="stat-value" style="color: {color if today_change < 0 else 'white'};">{sign}{today_change:,.2f}</div>
            <div class="stat-label">今日变动</div>
        </div>
        """, unsafe_allow_html=True)


def render_pie_chart():
    """渲染平台占比饼图"""
    stats = get_platform_stats()
    platforms = get_platforms()

    if not stats:
        return None

    # 构建数据
    labels = []
    values = []
    for pid, amount in stats.items():
        name = get_platform_name(pid)
        labels.append(name)
        values.append(amount)

    fig = px.pie(
        values=values,
        names=labels,
        title="各平台资金占比",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    return fig


def render_bar_chart():
    """渲染渠道分布柱状图"""
    stats = get_channel_stats()

    if not stats:
        return None

    labels = []
    values = []
    for cid, amount in stats.items():
        name = get_channel_name(cid)
        labels.append(name)
        values.append(amount)

    fig = px.bar(
        x=labels,
        y=values,
        title="各渠道资金分布",
        color=values,
        color_continuous_scale='Viridis'
    )
    fig.update_traces(texttemplate='¥%{y:,.0f}', textposition='outside')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="渠道类型",
        yaxis_title="金额 (元)",
        font=dict(size=14),
        showlegend=False
    )
    return fig


def render_trend_chart():
    """渲染趋势图"""
    history = get_recent_history(20)[::-1]  # 按时间正序

    if len(history) < 2:
        return None

    # 计算累计金额
    records = get_all_records()
    current_total = get_total_amount()

    times = []
    amounts = []
    total = current_total

    # 从最新往前推算
    for h in history[::-1]:
        times.append(h["changed_at"][:10])
        amounts.append(total)
        total -= h["change"]

    # 反转使时间正序
    times = times[::-1]
    amounts = amounts[::-1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=amounts,
        mode='lines+markers',
        name='总资产',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title="资产变动趋势",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="日期",
        yaxis_title="金额 (元)",
        font=dict(size=14),
        hovermode='x unified'
    )
    return fig


def render_recent_history():
    """渲染最近变动记录"""
    history = get_recent_history(5)

    if not history:
        st.info("暂无变动记录")
        return

    for h in history:
        record = None
        for r in get_all_records():
            if r["id"] == h["record_id"]:
                record = r
                break

        platform = get_platform_name(record["platform_id"]) if record else "已删除"
        change = h["change"]
        sign = "+" if change >= 0 else ""
        color = "#22c55e" if change >= 0 else "#ef4444"

        st.markdown(f"""
        <div class="history-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>{platform}</strong>
                    <span style="color:#666; font-size:0.85rem; margin-left:0.5rem;">
                        {h["changed_at"]}
                    </span>
                </div>
                <div style="color:{color}; font-weight:600; font-size:1.1rem;">
                    {sign}{change:,.2f}
                </div>
            </div>
            {f'<div style="color:#888; font-size:0.85rem; margin-top:0.3rem;">{h["note"]}</div>' if h["note"] else ''}
        </div>
        """, unsafe_allow_html=True)


def main():
    # 页面头部
    st.markdown("""
    <div class="page-header">
        <h1>💰 资金追踪</h1>
        <p>实时掌握资产动态</p>
    </div>
    """, unsafe_allow_html=True)

    # 快捷操作
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        if st.button("📝 资金管理", use_container_width=True):
            st.switch_page("pages/1_资金管理.py")
    with col2:
        if st.button("📊 变动历史", use_container_width=True):
            st.switch_page("pages/2_变动历史.py")
    with col3:
        if st.button("📈 统计报表", use_container_width=True):
            st.switch_page("pages/3_统计报表.py")

    st.markdown("---")

    # 统计卡片
    render_stats_cards()

    # 图表区域
    col1, col2 = st.columns(2)

    with col1:
        pie_fig = render_pie_chart()
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info("暂无数据，请先添加资金记录")

    with col2:
        bar_fig = render_bar_chart()
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.info("暂无数据，请先添加资金记录")

    # 趋势图
    trend_fig = render_trend_chart()
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)

    # 最近变动
    st.markdown("### 📋 最近变动")
    render_recent_history()


if __name__ == "__main__":
    main()