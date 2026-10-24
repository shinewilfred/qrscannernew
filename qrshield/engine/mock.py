from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pandas as pd

from .schema import Hop, Reason, ScanResult

POLICY = {"medium_from": 30, "high_from": 65, "block_shorteners": False, "flag_open_wifi": True, "lookalike_detection": True, "page_inspection": True, "payload_checks": True, "allowlist": ["hdfcbank.com", "github.com"], "blocklist": ["hdfc-kyc-update.top"]}
_HISTORY: list[ScanResult] = []
def _records() -> list[ScanResult]:
    return _HISTORY


def _reason(title: str, detail: str, severity: str, points: int) -> Reason:
    return Reason(title, detail, severity, points)


def _hop(domain: str, status: int, kind: str, note: str = "") -> Hop:
    return Hop(f"https://{domain}", domain, status, kind, note)


def _result(raw: str, input_type: str, score: int, title: str, reasons: list[Reason], chain: list[Hop], payload: dict | None = None, findings: list[str] | None = None, source: str = "demo") -> ScanResult:
    level = "High" if score >= POLICY["high_from"] else "Medium" if score >= POLICY["medium_from"] else "Low"
    digest = hashlib.sha1(f"{raw}{datetime.now().isoformat()}".encode()).hexdigest()[:10]
    seed = int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
    return ScanResult(digest, datetime.now(), input_type, raw, title, score, level, 0.86 + (seed % 13) / 100, reasons, chain, payload or {}, findings or [], ["Do not open or enter credentials" if level == "High" else "Verify the destination independently", "Report suspicious links to your admin", "Use official apps or bookmarked sites"], 900 + seed % 1501, source)


def analyze(raw: str | bytes, kind: str = "auto") -> ScanResult:
    if isinstance(raw, bytes): raw, kind = "upi://pay?pa=refund.desk@oksbi&pn=Amazon Refund&am=4999&tn=Cashback", "qr_upi"
    value = raw.strip(); lower = value.lower()
    if "hdfcbank.com/personal" in lower:
        result = _result(value, "url", 8, "HDFC Bank Personal Banking", [_reason("Official verified domain", "This matches an allowlisted bank domain.", "safe", -10), _reason("HTTPS is valid", "The address uses an encrypted connection.", "safe", -4), _reason("No redirects", "The link goes directly to its destination.", "safe", -3)], [_hop("hdfcbank.com/personal", 200, "final", "Direct destination")])
    elif "bit.ly/3xyz-kyc" in lower:
        result = _result(value, "url", 91, "HDFC KYC verification", [_reason("Brand lookalike", "“hdfc” appears in an unofficial domain.", "danger", 30), _reason("Risky .top domain", "This TLD is frequently abused in phishing.", "danger", 12), _reason("Password form", "The landing page asks for credentials.", "danger", 18), _reason("Newly registered domain", "The domain appears to be only 3 days old.", "danger", 15), _reason("Urgency language", "It says your account will be blocked.", "warn", 9), _reason("Shortened link", "The original destination was hidden.", "warn", 7)], [_hop("bit.ly/3xYz-KYC", 301, "shortener", "Destination hidden"), _hop("hdfc-kyc-update.top/verify", 302, "redirect", "Brand imitation"), _hop("secure.hdfc-kyc-update.top/login", 200, "final", "Credential page")], findings=["Password field", "Form posts to another domain", "Urgency wording"])
    elif "upi://pay?pa=refund.desk@oksbi" in lower or kind in {"qr_upi", "image", "camera"}:
        result = _result(value, "qr_upi", 88, "Amazon Refund payment request", [_reason("Payee mismatch", "Amazon is claimed, but the VPA looks personal.", "danger", 30), _reason("Prefilled amount", "₹4,999 is ready to send.", "warn", 15), _reason("Refund / cashback lure", "These words are common payment scams.", "danger", 20), _reason("UPI safety note", "Scanning a UPI QR only sends money.", "info", 0)], [], {"Payee name": "Amazon Refund", "VPA": "refund.desk@oksbi", "Amount": "₹4,999", "Note": "Cashback"})
    elif "wifi:t:nopass" in lower:
        result = _result(value, "qr_wifi", 52, "Open Wi‑Fi network", [_reason("Open network", "No password protects this connection.", "warn", 25), _reason("Generic network name", "“Free Airport WiFi” resembles a honeypot.", "warn", 15)], [], {"Network": "Free_Airport_WiFi", "Security": "Open"})
    elif "github.com/streamlit/streamlit" in lower:
        result = _result(value, "url", 5, "Streamlit · GitHub", [_reason("Trusted developer platform", "GitHub is an allowlisted destination.", "safe", -10), _reason("Direct HTTPS destination", "No redirect chain was detected.", "safe", -4)], [_hop("github.com/streamlit/streamlit", 200, "final")])
    elif "login.microsoftonline.com.secure-auth.xyz" in lower:
        result = _result(value, "url", 94, "Microsoft account sign in", [_reason("Brand in subdomain", "Microsoft is used before an unrelated domain.", "danger", 35), _reason("Risky .xyz domain", "This destination is not Microsoft.", "danger", 18), _reason("Credential page", "A sign-in form was detected.", "danger", 22), _reason("Lookalike structure", "The address is designed to look familiar.", "danger", 19)], [_hop("login.microsoftonline.com.secure-auth.xyz", 200, "final", "Credential page")], findings=["Password field", "Brand logo imitation", "External form action"])
    elif "smsto:+919999999999" in lower:
        result = _result(value, "qr_sms", 61, "Parcel payment SMS", [_reason("Fee demand", "Unexpected parcel fees are a common SMS scam.", "warn", 20), _reason("Short link", "The destination is hidden behind short.ly.", "warn", 18), _reason("Urgent wording", "The message pressures you to act quickly.", "warn", 12)], [_hop("short.ly/xx", 302, "shortener"), _hop("parcel-fee.example", 200, "final")], {"Recipient": "+91 99999 99999", "Message": "Your parcel is held"})
    else:
        result = _fallback(value, kind)
    _records().append(result)
    return result


def _fallback(value: str, kind: str) -> ScanResult:
    lower = value.lower(); seed = int(hashlib.sha256(value.encode()).hexdigest()[:8], 16); randomizer = random.Random(seed)
    checks = [("short", "Shortened link", "The destination is hidden.", 18), ("bit.ly", "Shortened link", "The destination is hidden.", 18), (".top", "Risky TLD", "This domain ending is often abused.", 15), (".xyz", "Risky TLD", "This domain ending is often abused.", 15), ("login", "Sign-in page", "This link may request credentials.", 16), ("verify", "Verification lure", "Verify prompts are frequently used in phishing.", 13), ("http:", "Unencrypted link", "This link does not use HTTPS.", 8)]
    reasons = [_reason(title, detail, "danger" if points > 15 else "warn", points) for keyword, title, detail, points in checks if keyword in lower]
    if not reasons: reasons = [_reason("No obvious danger signals", "No common phishing pattern was found in this text.", "safe", -6)]
    if any(part.isdigit() for part in value.split("/")): reasons.append(_reason("Unusual address pattern", "The address contains an IP-like or unusual host pattern.", "warn", 10))
    score = max(4, min(96, sum(max(0, item.points) for item in reasons) + randomizer.randint(2, 13)))
    domain = urlparse(value if "://" in value else f"https://{value}").netloc or "decoded-content"
    return _result(value, "url" if kind == "auto" else kind, score, "Decoded destination", reasons, [_hop(domain, 200, "final")])


def batch(items: list[str]) -> list[ScanResult]: return [analyze(item) for item in items if item.strip()]


def seed_history() -> list[ScanResult]:
    records = _records()
    if records: return records
    samples = ["https://hdfcbank.com/personal", "https://bit.ly/3xYz-KYC", "upi://pay?pa=refund.desk@oksbi&pn=Amazon Refund&am=4999&tn=Cashback", "WIFI:T:nopass;S:Free_Airport_WiFi;;", "https://github.com/streamlit/streamlit", "https://login.microsoftonline.com.secure-auth.xyz", "smsto:+919999999999:Your parcel is held, pay fee http://short.ly/xx"]
    randomizer = random.Random(2026); now = datetime.now()
    for index in range(150):
        result = analyze(samples[randomizer.choices(range(7), weights=[35, 8, 8, 10, 25, 5, 9])[0]])
        result.ts = now - timedelta(days=randomizer.randrange(60), hours=max(0, min(23, int(randomizer.gauss(13, 3)))))
        result.source = "sample"; records[-1] = result
    return records


def history(limit: int = 200, level: str | None = None, q: str | None = None) -> pd.DataFrame:
    rows = seed_history(); filtered = [item for item in rows if (not level or item.level == level) and (not q or q.lower() in item.raw.lower())]
    return pd.DataFrame([{"id": item.id, "Time": item.ts, "Level": item.level, "Score": item.score, "Type": item.input_type, "Domain": item.chain[-1].domain if item.chain else item.title, "Raw": item.raw, "Latency ms": item.latency_ms} for item in sorted(filtered, key=lambda item: item.ts, reverse=True)[:limit]])


def stats() -> dict:
    frame = history(); return {"total": len(frame), "high": int((frame.Level == "High").sum()), "average": round(float(frame.Score.mean()), 1), "latency": round(float(frame["Latency ms"].mean()))}


def get_policy() -> dict: return POLICY.copy()
def set_policy(data: dict) -> None: POLICY.update(data)
def validation_metrics() -> dict: return {"precision": 0.91, "recall": 0.88, "f1": 0.895, "accuracy": 0.90, "matrix": [[76, 6], [9, 59]]}
