"""设置页面 - 管理平台和渠道类型"""

import streamlit as st
from data_manager import (
    get_platforms, get_channel_types,
    add_platform, update_platform, delete_platform,
    add_channel_type, update_channel_type, delete_channel_type
)

st.set_page_config(
    page_title="设置 - 资金追踪",
    page_icon="⚙️",
    layout="wide",
)

# 常用图标
ICONS = ["💰", "💳", "🏦", "🏛️", "📈", "💵", "💎", "🔮", "🌟", "⭐", "🔥", "💪", "🎯", "📱", "💻", "🌍"]


def render_platform_management():
    """平台管理"""
    st.markdown("### 🏦 平台管理")

    platforms = get_platforms()

    # 添加新平台
    with st.expander("➕ 添加新平台"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("平台名称", placeholder="如：招商银行")
        with col2:
            new_icon = st.selectbox("图标", ICONS, index=0)

        if st.button("添加平台"):
            if new_name:
                add_platform(new_name, new_icon)
                st.success(f"已添加：{new_icon} {new_name}")
                st.rerun()
            else:
                st.error("请输入平台名称")

    # 现有平台列表
    if platforms:
        st.markdown("#### 已有平台")
        for p in platforms:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{p['icon']} {p['name']}**")
            with col2:
                if st.button("✏️", key=f"edit_p_{p['id']}", help="编辑"):
                    st.session_state[f"edit_platform_{p['id']}"] = True
            with col3:
                if st.button("🗑️", key=f"del_p_{p['id']}", help="删除"):
                    if delete_platform(p['id']):
                        st.success("已删除")
                        st.rerun()

            # 编辑模式
            if st.session_state.get(f"edit_platform_{p['id']}"):
                with st.form(f"form_p_{p['id']}"):
                    edit_name = st.text_input("名称", value=p['name'])
                    edit_icon = st.selectbox("图标", ICONS, index=ICONS.index(p['icon']) if p['icon'] in ICONS else 0)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("💾 保存"):
                            update_platform(p['id'], edit_name, edit_icon)
                            st.session_state[f"edit_platform_{p['id']}"] = False
                            st.rerun()
                    with col_b:
                        if st.form_submit_button("取消"):
                            st.session_state[f"edit_platform_{p['id']}"] = False
                            st.rerun()
    else:
        st.info("暂无平台，请添加")


def render_channel_management():
    """渠道类型管理"""
    st.markdown("### 🏷️ 渠道类型管理")

    channels = get_channel_types()

    # 添加新渠道
    with st.expander("➕ 添加新渠道类型"):
        new_name = st.text_input("渠道名称", placeholder="如：定期存款", key="new_channel")

        if st.button("添加渠道类型"):
            if new_name:
                add_channel_type(new_name)
                st.success(f"已添加：{new_name}")
                st.rerun()
            else:
                st.error("请输入渠道名称")

    # 现有渠道列表
    if channels:
        st.markdown("#### 已有渠道类型")
        for c in channels:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{c['name']}**")
            with col2:
                if st.button("✏️", key=f"edit_c_{c['id']}", help="编辑"):
                    st.session_state[f"edit_channel_{c['id']}"] = True
            with col3:
                if st.button("🗑️", key=f"del_c_{c['id']}", help="删除"):
                    if delete_channel_type(c['id']):
                        st.success("已删除")
                        st.rerun()

            # 编辑模式
            if st.session_state.get(f"edit_channel_{c['id']}"):
                with st.form(f"form_c_{c['id']}"):
                    edit_name = st.text_input("名称", value=c['name'])

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("💾 保存"):
                            update_channel_type(c['id'], edit_name)
                            st.session_state[f"edit_channel_{c['id']}"] = False
                            st.rerun()
                    with col_b:
                        if st.form_submit_button("取消"):
                            st.session_state[f"edit_channel_{c['id']}"] = False
                            st.rerun()
    else:
        st.info("暂无渠道类型，请添加")


def main():
    st.title("⚙️ 设置")

    # 返回按钮
    if st.button("← 返回首页"):
        st.switch_page("app.py")

    st.markdown("---")

    # Tab布局
    tab1, tab2 = st.tabs(["🏦 平台管理", "🏷️ 渠道类型"])

    with tab1:
        render_platform_management()

    with tab2:
        render_channel_management()


if __name__ == "__main__":
    main()