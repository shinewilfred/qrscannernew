from __future__ import annotations
from .mock import analyze as legacy_analyze
SAMPLES=("hdfcbank.com/personal","bit.ly/3xyz-kyc","upi://pay?pa=refund.desk@oksbi","wifi:t:nopass","github.com/streamlit/streamlit","login.microsoftonline.com.secure-auth.xyz","smsto:+919999999999")
def cached(raw: str):
    if any(item in raw.lower() for item in SAMPLES):
        result=legacy_analyze(raw); result.source="demo"; return result
    return None
