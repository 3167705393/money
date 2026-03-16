"""统计报表页面"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import StringIO
import csv
from data_manager import (
    get_all_records, get_all_history, get_platforms, get_channel_types,
    get_platform_name, get_channel_name, get_total_amount,
    get_platform_stats, get_channel_stats
)

st.set_page_config(
    page_title="统计报表 - 资金追踪",
    page_icon="📈",
    layout="wide",
)


def render_monthly_summary():
    """月度汇总"""
    history = get_all_history()
    records = get_all_records()

    # 按月统计
    monthly_data = {}
    for h in history:
        month = h['changed_at'][:7]  # YYYY-MM
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expense': 0, 'changes': []}
        if h['change'] > 0:
            monthly_data[month]['income'] += h['change']
        else:
            monthly_data[month]['expense'] += abs(h['change'])
        monthly_data[month]['changes'].append(h['change'])

    if not monthly_data:
        st.info("暂无历史数据")
        return None

    # 表格展示
    data = []
    for month in sorted(monthly_data.keys(), reverse=True):
        d = monthly_data[month]
        data.append({
            "月份": month,
            "收入": f"¥{d['income']:,.2f}",
            "支出": f"¥{d['expense']:,.2f}",
            "净变动": f"¥{d['income'] - d['expense']:,.2f}",
            "变动次数": len(d['changes'])
        })

    return data


def render_platform_comparison():
    """平台对比"""
    stats = get_platform_stats()

    if not stats:
        return None

    data = []
    for pid, amount in stats.items():
        data.append({
            "平台": get_platform_name(pid),
            "金额": amount
        })

    # 按金额排序
    data = sorted(data, key=lambda x: x['金额'], reverse=True)

    fig = px.bar(
        data,
        x='平台',
        y='金额',
        title='各平台资金对比',
        color='金额',
        color_continuous_scale='Blues'
    )
    fig.update_traces(texttemplate='¥%{y:,.0f}', textposition='outside')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14),
        showlegend=False
    )
    return fig


def render_channel_pie():
    """渠道饼图"""
    stats = get_channel_stats()

    if not stats:
        return None

    labels = []
    values = []
    for cid, amount in stats.items():
        labels.append(get_channel_name(cid))
        values.append(amount)

    fig = px.pie(
        values=values,
        names=labels,
        title='渠道资金分布',
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14)
    )
    return fig


def render_records_table():
    """详细记录表格"""
    records = get_all_records()

    if not records:
        return None

    data = []
    for r in records:
        data.append({
            "平台": get_platform_name(r['platform_id']),
            "渠道": get_channel_name(r['channel_type']),
            "金额": r['amount'],
            "备注": r.get('note', ''),
            "更新日期": r.get('updated_at', '')
        })

    return data


def export_to_csv(data: list, filename: str):
    """导出CSV"""
    if not data:
        return None

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def main():
    st.title("📈 统计报表")

    # 返回按钮
    if st.button("← 返回首页"):
        st.switch_page("app.py")

    st.markdown("---")

    # 总览
    total = get_total_amount()
    records = get_all_records()
    history = get_all_history()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总资产", f"¥{total:,.2f}")
    with col2:
        st.metric("账户数", len(records))
    with col3:
        st.metric("变动记录", len(history))

    st.markdown("---")

    # 月度汇总
    st.markdown("### 📅 月度汇总")
    monthly_data = render_monthly_summary()
    if monthly_data:
        st.table(monthly_data)

    st.markdown("---")

    # 图表
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 平台对比")
        platform_fig = render_platform_comparison()
        if platform_fig:
            st.plotly_chart(platform_fig, use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        st.markdown("### 🥧 渠道分布")
        channel_fig = render_channel_pie()
        if channel_fig:
            st.plotly_chart(channel_fig, use_container_width=True)
        else:
            st.info("暂无数据")

    st.markdown("---")

    # 详细记录
    st.markdown("### 📋 详细记录")
    records_data = render_records_table()
    if records_data:
        st.dataframe(records_data, use_container_width=True)

        # 导出按钮
        csv_data = export_to_csv(records_data, "资金记录.csv")
        if csv_data:
            st.download_button(
                "📥 导出CSV",
                csv_data,
                file_name=f"资金记录_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("暂无记录")


if __name__ == "__main__":
    main()