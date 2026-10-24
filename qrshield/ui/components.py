from __future__ import annotations
import html
import textwrap
import streamlit as st
from engine.schema import ScanResult
from ui.i18n import t

def _html(value: str) -> None: st.markdown(textwrap.dedent(value).strip(), unsafe_allow_html=True)
def pill(text: str, level: str = "info") -> str: return f'<span class="pill {level.lower()}">{html.escape(text)}</span>'
def kpi(label: str, value: str, detail: str = "") -> None: _html(f'<div class="metric-card"><strong>{value}</strong><span>{label}</span><small class="muted">{detail}</small></div>')
def empty_state() -> None: _html(f'<div class="scanner"><div>⌁<br><b>{t("waiting")}</b><br><small>{t("safe_distance")}</small></div></div>')
def pipeline() -> None: _html('<div class="glass pipeline">' + ''.join(f'<div class="pipe"><b>✓</b>{x}</div>' for x in ["Decode", "Trace redirects", "Inspect page", "Score", "Verdict"]) + '</div>')
def gauge(result: ScanResult) -> None:
    color = {"Low":"#22C55E","Medium":"#F59E0B","High":"#EF4444"}[result.level]; angle = -90 + result.score * 1.8
    _html(f'''<div class="result-card verdict" style="box-shadow:0 0 34px {color}22"><svg class="gauge" viewBox="0 0 210 120"><path d="M20 105 A85 85 0 0 1 190 105" fill="none" stroke="#22C55E" stroke-width="13"/><path d="M77 26 A85 85 0 0 1 144 35" fill="none" stroke="#F59E0B" stroke-width="13"/><path d="M145 36 A85 85 0 0 1 190 105" fill="none" stroke="#EF4444" stroke-width="13"/><g class="needle" style="--angle:{angle}deg"><path d="M105 105 L105 28" stroke="{color}" stroke-width="4"/><circle cx="105" cy="105" r="7" fill="{color}"/></g></svg><div><small class="muted">VERDICT</small><div class="score">{result.score}</div>{pill(t(result.level.lower()) + ' risk', result.level)} <span class="muted">Confidence {result.confidence:.0%}</span><h3>{'Do not open this link' if result.level == 'High' else 'Proceed with caution' if result.level == 'Medium' else 'Looks safe'}</h3><span class="muted">{html.escape(result.title)}</span></div></div>''')
def reason_cards(result: ScanResult) -> None:
    cards = ''.join(f'<div class="reason" style="border-color:{"#ef4444" if r.severity=="danger" else "#f59e0b" if r.severity=="warn" else "#22c55e" if r.severity=="safe" else "#22d3ee"}"><b>{html.escape(r.title)}</b><span class="points {r.severity}">{r.points:+d}</span><br><small class="muted">{html.escape(r.detail)}</small></div>' for r in result.reasons)
    _html(f'<h3>Why this score</h3><div class="reasons">{cards}</div>')
def timeline(result: ScanResult) -> None:
    if not result.chain: return
    rows = ''.join(f'<div class="hop"><span class="mono">{html.escape(hop.domain)}</span><br>{pill(str(hop.status), "info")} {pill({"shortener":"Short link","redirect":"Redirect","final":"Destination","start":"Start"}.get(hop.kind,hop.kind), "info")} <small class="muted">{html.escape(hop.note)}</small></div>' for hop in result.chain)
    _html(f'<h3>Redirect journey</h3><div class="timeline">{rows}<div class="hop"><b>🔒 Not opened. Analyzed safely.</b></div></div>')
def xray_card(result: ScanResult) -> None:
    findings = result.page_findings or ["No rendered page content", "Safe metadata inspection only"]
    _html(f'<h3>Page X-ray</h3><div class="result-card xray"><div class="browser">🔒 Not rendered · safe text preview only</div><p>{" ".join(pill(item, "info") for item in findings)}</p><small class="muted">Title: {html.escape(result.title)} · forms: {len(findings)} · scripts: 0 · iframes: 0</small></div>')
def payload_card(result: ScanResult) -> None:
    if not result.payload: return
    rows = ''.join(f'<div class="payload-row"><span class="muted">{html.escape(str(key))}</span><b>{html.escape(str(value))}</b></div>' for key,value in result.payload.items())
    banner = '<p class="warn-banner">⚠ Scanning a UPI QR only ever SENDS money. You never scan to receive.</p>' if result.input_type == "qr_upi" else ""
    _html(f'<h3>Payload decoder</h3><div class="result-card xray">{banner}{rows}</div>')
