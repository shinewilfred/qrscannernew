from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from engine import history, stats
from ui.components import kpi
from ui.i18n import t

COLORS = {"Low":"#22C55E", "Medium":"#F59E0B", "High":"#EF4444"}
def _chart(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=35,b=10), transition_duration=500, font_color="#E6EDF7")
    st.plotly_chart(fig, use_container_width=True)
def render() -> None:
    if not st.session_state.get("admin_ok"):
        st.markdown('<div class="scanner"><div style="font-size:2rem">🔒<br><b>Admin console</b></div></div>', unsafe_allow_html=True)
        pin = st.text_input(t("pin"), type="password", key="admin_pin")
        if st.button(t("unlock"), type="primary", key="unlock_admin"):
            if pin == "2026": st.session_state.admin_ok = True; st.rerun()
            else: st.error(t("incorrect_pin"))
        return
    st.title(t("admin_title"))
    metrics = stats(); cols = st.columns(4)
    for column, label, value in zip(cols, ["Total scans", "High-risk blocked", "Average risk", "Average verdict time"], [metrics["total"], metrics["high"], metrics["average"], f'{metrics["latency"]}ms']):
        with column: kpi(label, str(value))
    include_sample = st.toggle(t("include_sample"), value=True, key="include_sample")
    frame = history(200)
    if not include_sample and "Raw" in frame: frame = frame[~frame.id.astype(str).str.startswith("sample-")]
    frame["Date"] = pd.to_datetime(frame["Time"]).dt.date; frame["Hour"] = pd.to_datetime(frame["Time"]).dt.hour
    left, right = st.columns(2)
    with left: _chart(px.pie(frame, names="Level", color="Level", color_discrete_map=COLORS, hole=.62, title="Risk levels"))
    with right: _chart(px.area(frame.groupby(["Date","Level"]).size().reset_index(name="Scans"), x="Date", y="Scans", color="Level", color_discrete_map=COLORS, title="Scans over time"))
    left, right = st.columns(2)
    with left: _chart(px.bar(frame.groupby("Domain").Score.mean().nlargest(8).sort_values().reset_index(), x="Score", y="Domain", orientation="h", title="Riskiest destinations", color_discrete_sequence=["#EF4444"]))
    with right: _chart(px.bar(frame.groupby("Type").size().reset_index(name="Scans"), x="Type", y="Scans", title="Input types", color_discrete_sequence=["#22D3EE"]))
    heat = frame.groupby(["Hour","Level"]).size().unstack(fill_value=0)
    _chart(px.imshow(heat.T, color_continuous_scale=[[0,"#071420"],[1,"#22D3EE"]], title="Hour-of-day heatmap", aspect="auto"))
    st.subheader(t("live_feed"))
    levels = st.multiselect(t("level"), ["Low","Medium","High"], default=["Low","Medium","High"], key="admin_levels")
    query = st.text_input(t("search"), key="admin_search")
    shown = frame[frame.Level.isin(levels)]
    if query: shown = shown[shown.Raw.str.contains(query, case=False, na=False)]
    st.dataframe(shown[["Time","Level","Score","Type","Domain"]], use_container_width=True, hide_index=True)
    st.download_button(t("export"), shown.to_csv(index=False), "qrshield-history.csv", key="admin_export")

if __name__ == "__main__": render()
