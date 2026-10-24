import streamlit as st
from engine import get_policy, set_policy
from ui.pages.scan import SAMPLES
from ui.components import pill
from ui.i18n import t

def render() -> None:
    st.title(t("policy_title"))
    policy = get_policy()
    left, right = st.columns(2)
    with left:
        medium = st.slider(t("medium_from"), 1, 90, policy["medium_from"], key="medium_from")
        high = st.slider(t("high_from"), medium + 1, 100, max(policy["high_from"], medium + 1), key="high_from")
    with right:
        policy["block_shorteners"] = st.toggle(t("block_shorteners"), policy["block_shorteners"], key="block_shorteners")
        policy["flag_open_wifi"] = st.toggle(t("flag_wifi"), policy["flag_open_wifi"], key="flag_open_wifi")
        policy["lookalike_detection"] = st.toggle(t("lookalike"), policy["lookalike_detection"], key="lookalike")
        policy["page_inspection"] = st.toggle(t("inspection"), policy["page_inspection"], key="inspection")
        policy["payload_checks"] = st.toggle(t("payload_checks"), policy["payload_checks"], key="payload_checks")
    st.subheader(t("preview"))
    scores = [8,91,88,52,61,94]
    preview = " ".join(pill(f"{name} {score}", "high" if score >= high else "medium" if score >= medium else "low") for (name,_),score in zip(SAMPLES.items(),scores))
    st.markdown(preview, unsafe_allow_html=True)
    st.subheader(t("lists"))
    allow = st.data_editor([{ "Domain": item } for item in policy["allowlist"]], key="allow_editor", num_rows="dynamic")
    block = st.data_editor([{ "Domain": item } for item in policy["blocklist"]], key="block_editor", num_rows="dynamic")
    if st.button(t("save_policy"), type="primary", key="save_policy"):
        policy.update({"medium_from":medium,"high_from":high,"allowlist":[x["Domain"] for x in allow if x.get("Domain")],"blocklist":[x["Domain"] for x in block if x.get("Domain")]}); set_policy(policy); st.toast(t("policy_saved"))

if __name__ == "__main__": render()
