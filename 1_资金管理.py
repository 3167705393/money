"""资金管理页面"""

import streamlit as st
from data_manager import (
    get_all_records, get_platforms, get_channel_types,
    add_record, update_record, delete_record,
    get_platform_name, get_channel_name
)

st.set_page_config(
    page_title="资金管理 - 资金追踪",
    page_icon="📝",
    layout="wide",
)

st.markdown("""
<style>
    .record-card {
        background: white; border-radius: 12px; padding: 1rem;
        margin-bottom: 0.8rem; border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .record-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 0.5rem;
    }
    .amount-display {
        font-size: 1.5rem; font-weight: 700; color: #667eea;
    }
</style>
""", unsafe_allow_html=True)


def render_add_form():
    """渲染添加记录表单"""
    platforms = get_platforms()
    channel_types = get_channel_types()

    if not platforms:
        st.warning("请先在设置页面添加平台")
        return

    if not channel_types:
        st.warning("请先在设置页面添加渠道类型")
        return

    with st.expander("➕ 添加新记录", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            platform_options = {f"{p['icon']} {p['name']}": p['id'] for p in platforms}
            platform = st.selectbox("平台", list(platform_options.keys()))
            platform_id = platform_options[platform]

        with col2:
            channel_options = {c['name']: c['id'] for c in channel_types}
            channel = st.selectbox("渠道类型", list(channel_options.keys()))
            channel_id = channel_options[channel]

        with col3:
            amount = st.number_input("金额", min_value=0.0, step=100.0, value=0.0)

        note = st.text_input("备注", placeholder="可选，如：日常消费账户")

        if st.button("✅ 添加记录", type="primary"):
            if amount <= 0:
                st.error("金额必须大于0")
            else:
                add_record(platform_id, channel_id, amount, note)
                st.success("添加成功！")
                st.rerun()


def render_records_list():
    """渲染记录列表"""
    records = get_all_records()

    if not records:
        st.info("暂无记录，点击上方「添加新记录」开始")
        return

    # 筛选
    platforms = get_platforms()
    platform_filter = st.selectbox(
        "筛选平台",
        ["全部"] + [p['name'] for p in platforms]
    )

    filtered = records
    if platform_filter != "全部":
        pid = next((p['id'] for p in platforms if p['name'] == platform_filter), None)
        if pid:
            filtered = [r for r in records if r['platform_id'] == pid]

    # 记录卡片
    for record in filtered:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown(f"**{get_platform_name(record['platform_id'])}**")
                st.caption(f"渠道: {get_channel_name(record['channel_type'])}")

            with col2:
                st.markdown(f"<span style='font-size:1.3rem; font-weight:600; color:#667eea;'>¥{record['amount']:,.2f}</span>", unsafe_allow_html=True)

            with col3:
                if record.get('note'):
                    st.caption(f"📝 {record['note']}")
                st.caption(f"更新: {record.get('updated_at', '-')}")

            with col4:
                # 编辑按钮
                if st.button("✏️", key=f"edit_{record['id']}", help="编辑"):
                    st.session_state.editing = record['id']

            # 编辑模式
            if st.session_state.get('editing') == record['id']:
                with st.form(f"form_{record['id']}"):
                    new_amount = st.number_input("新金额", value=float(record['amount']), step=100.0)
                    new_note = st.text_input("备注", value=record.get('note', ''))

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("💾 保存"):
                            update_record(record['id'], amount=new_amount, note=new_note)
                            st.session_state.editing = None
                            st.rerun()
                    with col_b:
                        if st.form_submit_button("❌ 取消"):
                            st.session_state.editing = None
                            st.rerun()

            # 删除确认
            if st.session_state.get('deleting') == record['id']:
                st.warning("确定要删除这条记录吗？")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🗑️ 确认删除", key=f"confirm_{record['id']}"):
                        delete_record(record['id'])
                        st.session_state.deleting = None
                        st.rerun()
                with col_b:
                    if st.button("取消", key=f"cancel_{record['id']}"):
                        st.session_state.deleting = None
                        st.rerun()
            else:
                if st.button("🗑️", key=f"del_{record['id']}", help="删除"):
                    st.session_state.deleting = record['id']
                    st.rerun()

            st.markdown("---")


def main():
    st.title("📝 资金管理")

    # 返回按钮
    if st.button("← 返回首页"):
        st.switch_page("app.py")

    st.markdown("---")

    # 添加表单
    render_add_form()

    # 记录列表
    st.markdown("### 📋 资金记录")
    render_records_list()


if __name__ == "__main__":
    main()