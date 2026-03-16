"""变动历史页面"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_manager import (
    get_all_history, get_all_records, get_platforms,
    get_platform_name
)

st.set_page_config(
    page_title="变动历史 - 资金追踪",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    .history-card {
        background: #f8f9ff; border-radius: 12px; padding: 1rem;
        margin-bottom: 0.8rem; border-left: 4px solid;
    }
    .positive { border-color: #22c55e; }
    .negative { border-color: #ef4444; }
</style>
""", unsafe_allow_html=True)


def render_filters():
    """渲染筛选器"""
    col1, col2, col3 = st.columns(3)

    with col1:
        platforms = get_platforms()
        platform_options = ["全部"] + [p['name'] for p in platforms]
        selected_platform = st.selectbox("平台", platform_options)

    with col2:
        date_range = st.date_input(
            "日期范围",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )

    with col3:
        change_type = st.selectbox("变动类型", ["全部", "增加", "减少"])

    return selected_platform, date_range, change_type


def filter_history(history, platform_filter, date_range, change_type):
    """筛选历史记录"""
    records = {r['id']: r for r in get_all_records()}
    platforms = {p['id']: p['name'] for p in get_platforms()}

    filtered = []
    for h in history:
        record = records.get(h['record_id'])
        if not record:
            continue

        # 平台筛选
        if platform_filter != "全部":
            if platforms.get(record['platform_id']) != platform_filter:
                continue

        # 日期筛选
        if len(date_range) == 2:
            start, end = date_range
            h_date = datetime.strptime(h['changed_at'][:10], "%Y-%m-%d").date()
            if h_date < start or h_date > end:
                continue

        # 变动类型筛选
        if change_type == "增加" and h['change'] <= 0:
            continue
        if change_type == "减少" and h['change'] >= 0:
            continue

        filtered.append(h)

    return filtered


def render_history_list(history):
    """渲染历史列表"""
    records = {r['id']: r for r in get_all_records()}

    if not history:
        st.info("没有符合条件的记录")
        return

    for h in history:
        record = records.get(h['record_id'])
        if not record:
            continue

        change = h['change']
        sign = "+" if change >= 0 else ""
        color = "#22c55e" if change >= 0 else "#ef4444"
        css_class = "positive" if change >= 0 else "negative"

        st.markdown(f"""
        <div class="history-card {css_class}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="font-size:1.1rem;">{get_platform_name(record['platform_id'])}</strong>
                    <span style="color:#666; margin-left:1rem;">{h['changed_at']}</span>
                </div>
                <div style="color:{color}; font-weight:700; font-size:1.2rem;">
                    {sign}{change:,.2f}
                </div>
            </div>
            <div style="margin-top:0.5rem; color:#666;">
                <span>变动前: ¥{h['old_amount']:,.2f}</span>
                <span style="margin-left:1rem;">变动后: ¥{h['new_amount']:,.2f}</span>
            </div>
            {f'<div style="margin-top:0.3rem; color:#888;">📝 {h["note"]}</div>' if h.get('note') else ''}
        </div>
        """, unsafe_allow_html=True)


def render_trend_chart(history):
    """渲染变动趋势图"""
    if len(history) < 2:
        return None

    # 按日期分组统计
    daily_changes = {}
    for h in history:
        date = h['changed_at'][:10]
        daily_changes[date] = daily_changes.get(date, 0) + h['change']

    dates = list(daily_changes.keys())[::-1]
    changes = list(daily_changes.values())[::-1]
    cumulative = []
    total = 0
    for c in changes:
        total += c
        cumulative.append(total)

    fig = go.Figure()

    # 变动柱状图
    colors = ['#22c55e' if c >= 0 else '#ef4444' for c in changes]
    fig.add_trace(go.Bar(
        x=dates,
        y=changes,
        name='日变动',
        marker_color=colors
    ))

    fig.update_layout(
        title="每日变动趋势",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="日期",
        yaxis_title="变动金额 (元)",
        font=dict(size=14),
        barmode='relative'
    )

    return fig


def main():
    st.title("📊 变动历史")

    # 返回按钮
    if st.button("← 返回首页"):
        st.switch_page("app.py")

    st.markdown("---")

    # 筛选器
    platform_filter, date_range, change_type = render_filters()

    # 获取并筛选数据
    all_history = get_all_history()
    filtered_history = filter_history(all_history, platform_filter, date_range, change_type)

    # 统计
    if filtered_history:
        total_change = sum(h['change'] for h in filtered_history)
        positive = sum(1 for h in filtered_history if h['change'] > 0)
        negative = sum(1 for h in filtered_history if h['change'] < 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            sign = "+" if total_change >= 0 else ""
            color = "green" if total_change >= 0 else "red"
            st.metric("净变动", f"{sign}{total_change:,.2f}")
        with col2:
            st.metric("增加次数", positive)
        with col3:
            st.metric("减少次数", negative)

        st.markdown("---")

        # 趋势图
        trend_fig = render_trend_chart(filtered_history)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)

    # 历史列表
    st.markdown("### 📋 变动记录")
    render_history_list(filtered_history)


if __name__ == "__main__":
    main()