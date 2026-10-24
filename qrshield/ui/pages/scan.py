from __future__ import annotations
import time
import streamlit as st
from engine import analyze
from engine.input import clean_link
from engine.report import html_report
from ui.i18n import t
from ui.components import empty_state, gauge, payload_card, pipeline, reason_cards, timeline, xray_card

SAMPLES = {"✅ Bank site":"https://hdfcbank.com/personal", "🚨 Short KYC link":"https://bit.ly/3xYz-KYC", "💸 Fake UPI refund":"upi://pay?pa=refund.desk@oksbi&pn=Amazon Refund&am=4999&tn=Cashback", "📶 Open Wi-Fi":"WIFI:T:nopass;S:Free_Airport_WiFi;;", "📩 Parcel SMS":"smsto:+919999999999:Your parcel is held, pay fee http://short.ly/xx", "🔐 Fake Microsoft login":"https://login.microsoftonline.com.secure-auth.xyz"}

def _run(value: str, kind: str = "auto") -> None:
    placeholder = st.empty(); pipeline(); time.sleep(2.25); placeholder.empty()
    st.session_state["last_result"] = analyze(value, kind); st.session_state["animated_id"] = st.session_state["last_result"].id

def _select_sample(value: str) -> None:
    st.session_state["scan_link"] = value
    st.session_state["scan_pending"] = True

def _submit_link(value: str) -> None:
    link, remaining, error = clean_link(value)
    if error:
        st.error(t("invalid_link") if t("invalid_link") != "invalid_link" else error)
        return
    if remaining:
        st.session_state["batch_text"] = "\n".join(remaining)
        st.info(t("extra_links") if t("extra_links") != "extra_links" else "Additional links are ready in Batch.")
    _run(link)

def render() -> None:
    st.title(t("scan_safely"))
    left, right = st.columns([5, 7], gap="large")
    with left:
        st.markdown('<div class="glass" style="padding:1rem">', unsafe_allow_html=True)
        st.subheader(t("input"))
        link, camera, upload, message = st.tabs([t("link"), t("camera"), t("upload_qr"), t("message")])
        with link:
            if "selected_chip" in st.session_state:
                _select_sample(st.session_state.pop("selected_chip"))
            with st.form("scan_form", clear_on_submit=False):
                raw = st.text_input(t("link"), placeholder=t("link_placeholder"), label_visibility="collapsed", key="scan_link")
                submitted = st.form_submit_button(t("analyze"), type="primary", use_container_width=True)
            if submitted: _submit_link(raw)
            sample_cols = st.columns(2)
            for index, (label, value) in enumerate(SAMPLES.items()):
                sample_cols[index % 2].button(label, key=f"chip_{index}", use_container_width=True, on_click=_select_sample, args=(value,))
            if st.session_state.pop("scan_pending", False): _submit_link(st.session_state["scan_link"])
        with camera:
            image = st.camera_input(t("capture_qr"), key="camera_qr")
            if image and st.button(t("analyze_camera"), type="primary", key="camera_analyze"): _run(image.getvalue(), "camera")
        with upload:
            image = st.file_uploader(t("upload_image"), type=["png", "jpg", "jpeg"], key="qr_upload")
            if image: st.image(image, caption="Safe local decode preview")
            if image and st.button(t("analyze_upload"), type="primary", key="upload_analyze"): _run(image.getvalue(), "image")
        with message:
            text = st.text_area(t("paste_message"), placeholder=t("message_placeholder"), key="scan_message")
            if st.button(t("extract"), key="extract_links"):
                st.session_state["batch_text"] = text; st.switch_page("ui/pages/batch.py")
        st.caption(t("safe_distance"))
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        result = st.session_state.get("last_result")
        if not result: empty_state(); return
        gauge(result); reason_cards(result); timeline(result); xray_card(result); payload_card(result)
        st.markdown(f"### {t('what_now')}")
        for action in result.actions: st.checkbox(action, key=f"action_{result.id}_{action}")
        buttons = st.columns(4)
        for column, label in zip(buttons, [t("report"), t("false_positive"), t("download"), t("copy")]):
            if column.button(label, key=f"{label}_{result.id}"):
                if label == t("download"): column.download_button("Save HTML", html_report(result), "qrshield-report.html", key=f"save_{result.id}")
                else: st.toast(t("recorded", label=label))

if __name__ == "__main__": render()
