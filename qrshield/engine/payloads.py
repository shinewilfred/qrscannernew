from __future__ import annotations
from urllib.parse import parse_qs, unquote
from .lexical import extract_urls

def classify(raw: str) -> str:
    lower=raw.lower()
    if lower.startswith("upi://"): return "qr_upi"
    if lower.startswith("wifi:"): return "qr_wifi"
    if lower.startswith(("smsto:","sms:")): return "qr_sms"
    if lower.startswith("mailto:"): return "email"
    if lower.startswith(("http://","https://","hxxp://","hxxps://","www.")): return "url"
    return "qr_text"
def parse(raw: str) -> dict:
    kind=classify(raw); lower=raw.lower()
    if kind=="qr_upi":
        query=parse_qs(raw.split("?",1)[1] if "?" in raw else ""); return {"Payee name":query.get("pn",[""])[0],"VPA":query.get("pa",[""])[0],"Amount":f"₹{query.get('am',[''])[0]}" if query.get("am") else "Not set","Note":query.get("tn",[""])[0]}
    if kind=="qr_wifi":
        fields=dict(part.split(":",1) for part in raw[5:].split(";") if ":" in part); return {"Network":unquote(fields.get("S","")),"Security":fields.get("T","nopass")}
    if kind=="qr_sms": return {"Message":raw.split(":",2)[-1],"URLs":", ".join(extract_urls(raw))}
    return {}
