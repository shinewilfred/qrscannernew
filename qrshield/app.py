from __future__ import annotations
import streamlit as st
from ui.theme import inject_theme
from ui.i18n import LANGUAGES, set_language, t

st.set_page_config(layout="wide", page_title="QRShield", page_icon="🛡️", initial_sidebar_state="collapsed")
inject_theme()
if "demo_mode" not in st.session_state: st.session_state.demo_mode = True

status = "Demo" if st.session_state.demo_mode else "Live"
status_class = "#22D3EE" if st.session_state.demo_mode else "#22C55E"
st.markdown(f'''<div class="nav"><div class="brand"><span class="shield">🛡️</span><span class="gradient-text">QRShield</span></div><span class="nav-status" style="color:{status_class}">● Engine: {status}</span></div>''', unsafe_allow_html=True)
top_left, language_column, top_right = st.columns([6,2,2])
with language_column:
    selected = st.selectbox(t("language"), list(LANGUAGES), format_func=lambda code: LANGUAGES[code], index=list(LANGUAGES).index(st.session_state.get("language", "en")), key="language_selector")
    set_language(selected)
with top_right: st.toggle(t("demo_mode"), key="demo_mode")

pages = [
    st.Page("ui/pages/home.py", title=t("home"), icon="🏠", default=True),
    st.Page("ui/pages/scan.py", title=t("scan"), icon="🔎"),
    st.Page("ui/pages/batch.py", title=t("batch"), icon="📋"),
    st.Page("ui/pages/admin.py", title=t("admin"), icon="🛡️"),
    st.Page("ui/pages/policy.py", title=t("policy"), icon="⚙️"),
    st.Page("ui/pages/trust.py", title=t("trust"), icon="✅"),
]
try:
    navigation = st.navigation(pages, position="top")
except TypeError:
    navigation = st.navigation(pages)
navigation.run()
