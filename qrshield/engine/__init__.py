from __future__ import annotations
import hashlib, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pandas as pd
from .decode import decode_image
from .demo_cache import cached
from .lexical import extract_urls, normalized, registered_domain
from .ml import probability
from .page import inspect
from .payloads import classify, parse
from .policy import get_policy, set_policy
from .resolve import resolve
from .schema import Hop, Reason, ScanResult
from .scoring import final_score, lexical_reasons, payload_reasons, trusted_domain
from .store import frame, save
from .validate import metrics as _metrics

def _result(raw, kind, reasons, chain, payload, findings, title, source, started):
    score,level,confidence=final_score(reasons,probability(raw) if kind=="url" else 0,get_policy(),raw if kind=="url" else "")
    result=ScanResult(hashlib.sha1(f"{raw}{time.time_ns()}".encode()).hexdigest()[:12],datetime.now(),kind,raw,title or "Decoded content",score,level,confidence,sorted(reasons,key=lambda item:item.points,reverse=True),chain,payload,findings,["Do not open or enter credentials" if level=="High" else "Verify the destination independently","Report suspicious content to your admin","Use the official app or bookmarked site"],int((time.monotonic()-started)*1000),source)
    save(result); return result
def _live(raw, kind="auto"):
    started=time.monotonic(); input_type=classify(raw) if kind=="auto" else kind; payload=parse(raw); reasons=payload_reasons(input_type,payload); chain=[]; findings=[]; title=""
    if input_type=="url":
        url=normalized(raw); reasons.extend(lexical_reasons(url))
        try:
            if trusted_domain(registered_domain(url)):
                reasons.append(Reason("No suspicious redirects","This official domain was checked without following an untrusted destination.","safe",-2))
                chain=[Hop(url, url.split("/")[2], 200, "final", "Trusted official domain")]
                html=""; final_url=url; network_findings=[]
            else: chain,html,final_url,network_findings=resolve(url)
            findings.extend(network_findings); page_reasons,page_findings,title=inspect(html,final_url); reasons.extend(page_reasons); findings.extend(page_findings)
            if len(chain)>=3: reasons.append(Reason("Long redirect chain","This link passed through three or more destinations.","warn",10))
            if len({'.'.join(item.domain.split('.')[-2:]) for item in chain if item.domain.count('.')})>=2: reasons.append(Reason("Cross-domain redirect","The journey crosses registered domains.","warn",8))
            if any("Meta" in item.note for item in chain): reasons.append(Reason("Script redirect","The page requested a meta or JavaScript redirect.","warn",10))
        except Exception as exc: reasons.append(Reason("Could not verify remotely",f"{exc}. Offline risk checks were still completed.","info",0)); findings.append("Remote inspection unavailable")
    elif extract_urls(raw): reasons.append(Reason("Embedded link found","The QR content contains a link that should be checked separately.","warn",8)); title="Message or text payload"
    elif input_type=="qr_wifi": title="Wi‑Fi configuration"
    elif input_type=="qr_upi": title="UPI payment request"
    else: title="Decoded text"
    return _result(raw,input_type,reasons,chain,payload,findings,title,"live",started)
def analyze(raw: str | bytes, kind: str="auto") -> ScanResult:
    if isinstance(raw,bytes):
        try: value,detected=decode_image(raw)[0]; return analyze(value,detected)
        except Exception as exc: return _result("[image]","qr_text",[Reason("Could not decode QR",str(exc),"warn",6)],[],{},[],"QR image","live",time.monotonic())
    value=raw.strip(); sample=cached(value)
    if sample: save(sample); return sample
    try: return _live(value,kind)
    except Exception as exc: return _result(value,"qr_text",[Reason("Could not fully analyze",str(exc),"warn",6)],[],{},[],"Analysis unavailable","demo",time.monotonic())
def batch(items: list[str]) -> list[ScanResult]:
    values=[]
    for item in items: values.extend(extract_urls(item) or ([item] if item.strip() else []))
    with ThreadPoolExecutor(max_workers=5) as pool: return sorted(pool.map(analyze,dict.fromkeys(values)),key=lambda item:item.score,reverse=True)
def _seed_samples() -> None:
    if len(frame(1)): return
    from datetime import timedelta
    samples=["https://hdfcbank.com/personal","https://bit.ly/3xYz-KYC","upi://pay?pa=refund.desk@oksbi&pn=Amazon Refund&am=4999&tn=Cashback","WIFI:T:nopass;S:Free_Airport_WiFi;;","https://github.com/streamlit/streamlit","https://login.microsoftonline.com.secure-auth.xyz","smsto:+919999999999:Your parcel is held, pay fee http://short.ly/xx"]
    for index in range(150):
        result=cached(samples[index%len(samples)]); result.id=f"sample-{index}"; result.ts=datetime.now()-timedelta(days=index%60,hours=8+(index%10)); result.source="sample"; save(result)
def history(limit=200,level=None,q=None) -> pd.DataFrame:
    _seed_samples(); return frame(limit,level,q)
def stats() -> dict:
    _seed_samples(); data=frame(); return {"total":len(data),"high":int((data.Level=="High").sum()) if len(data) else 0,"average":round(float(data.Score.mean()),1) if len(data) else 0,"latency":round(float(data["Latency ms"].mean())) if len(data) else 0}
def validation_metrics() -> dict: return _metrics()

__all__=["analyze","batch","history","stats","get_policy","set_policy","validation_metrics"]
