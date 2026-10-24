import streamlit as st
from ui.components import kpi

def render() -> None:
    st.markdown('''<div class="hero"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="eyebrow">PS07 · Pre-click protection</div><div style="display:grid;grid-template-columns:1.15fr .85fr;gap:2rem;align-items:center"><div><h1 style="font-size:clamp(2.8rem,6vw,5.5rem);margin:.5rem 0">Think before you <span class="gradient-text">scan.</span></h1><p class="muted" style="font-size:1.15rem;max-width:540px">Know where a link or QR code leads, before anyone opens it.</p></div><svg class="hero-svg" viewBox="0 0 400 300"><circle cx="205" cy="145" r="105" fill="none" stroke="#22d3ee44" stroke-width="2"/><circle cx="205" cy="145" r="82" fill="none" stroke="#8b5cf644" stroke-width="2"/><path d="M205 45l82 32v62c0 58-42 91-82 111-40-20-82-53-82-111V77z" fill="#ffffff08" stroke="#22d3ee" stroke-width="4"/><g fill="#22d3ee"><rect x="158" y="96" width="22" height="22"/><rect x="228" y="96" width="22" height="22"/><rect x="158" y="166" width="22" height="22"/><rect x="192" y="130" width="18" height="18"/><rect x="222" y="150" width="24" height="18"/><rect x="188" y="174" width="16" height="16"/></g><rect class="scanline" x="145" y="85" width="120" height="3" fill="#22d3ee"/></svg></div><div class="stat-strip"><div class="metric-card"><strong>0</strong><small>pages ever opened</small></div><div class="metric-card"><strong>20+</strong><small>risk signals</small></div><div class="metric-card"><strong>7</strong><small>QR payload types</small></div><div class="metric-card"><strong>&lt;3s</strong><small>average verdict</small></div></div></div>''', unsafe_allow_html=True)
    first, second = st.columns(2)
    with first:
        if st.button("Scan something now", type="primary", key="home_scan"): st.switch_page("ui/pages/scan.py")
    with second:
        if st.button("Watch a live demo", key="home_demo"):
            st.session_state["selected_chip"] = "https://bit.ly/3xYz-KYC"; st.switch_page("ui/pages/scan.py")
    st.markdown("## How it works")
    st.markdown('''<div class="steps"><div class="step-card"><span class="badge">1</span><h3>Decode</h3><small class="muted">Read QR payloads safely.</small></div><div class="step-card"><span class="badge">2</span><h3>Trace</h3><small class="muted">Map redirects without visiting.</small></div><div class="step-card"><span class="badge">3</span><h3>Inspect</h3><small class="muted">Check risk signals remotely.</small></div><div class="step-card"><span class="badge">4</span><h3>Explain</h3><small class="muted">Give a clear next action.</small></div></div>''', unsafe_allow_html=True)
    st.markdown("## A real scam, stopped")
    st.markdown('''<div class="result-card verdict"><div style="font-size:5rem;text-align:center">▦<br><small style="font-size:.8rem">Amazon refund QR</small></div><div><span class="risk high">High · 88</span><h3>UPI refund payment request</h3><p class="muted">The VPA is personal, and ₹4,999 is prefilled.</p><span class="pill danger">Payee mismatch +30</span> <span class="pill warn">Refund lure +20</span></div></div><div class="footer">Built for QUANTIX 2K26 · PS07 QRShield</div>''', unsafe_allow_html=True)

if __name__ == "__main__": render()
