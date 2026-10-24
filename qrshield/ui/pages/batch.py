from __future__ import annotations
import re
import streamlit as st
from engine import batch
from ui.components import kpi
from ui.i18n import t

def render() -> None:
    st.title(t("batch_scan"))
    text = st.text_area(t("batch_placeholder"), value=st.session_state.pop("batch_text", ""), height=150, key="batch_textarea")
    upload = st.file_uploader(t("upload_file"), type=["txt", "csv"], key="batch_upload")
    if upload: text = upload.getvalue().decode("utf-8", errors="ignore")
    if st.button(t("scan_all"), type="primary", key="batch_scan"):
        items = re.findall(r"(?:https?://|upi://|smsto:|WIFI:)[^\s,]+", text, re.I) or [line for line in text.splitlines() if line.strip()]
        bar = st.progress(0); results = []
        for index, item in enumerate(items): results.extend(batch([item])); bar.progress((index + 1) / max(1, len(items)))
        st.session_state["batch_results"] = results
    results = st.session_state.get("batch_results", [])
    if not results: return
    counts = {level: sum(item.level == level for item in results) for level in ["High", "Medium", "Low"]}
    row = st.columns(4)
    for col, label, value in zip(row, ["Links found", "High", "Medium", "Low"], [len(results), counts["High"], counts["Medium"], counts["Low"]]):
        with col: kpi(label, str(value))
    data = [{"Level": item.level, "Score": item.score, "Destination": item.chain[-1].domain if item.chain else item.title, "Type": item.input_type} for item in sorted(results, key=lambda item: item.score, reverse=True)]
    st.dataframe(data, use_container_width=True, hide_index=True, column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100)})
    st.download_button(t("export"), "\n".join("%s,%s,%s" % (row["Level"], row["Score"], row["Destination"]) for row in data), "qrshield-batch.csv", key="batch_export")
    for item in results:
        with st.expander(f"{item.level} · {item.title} · {item.score}"):
            st.write(" · ".join(reason.title for reason in item.reasons[:3]))

if __name__ == "__main__": render()
