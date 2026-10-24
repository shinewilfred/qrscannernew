from __future__ import annotations
import ipaddress, socket, time
from functools import lru_cache
from urllib.parse import urljoin, urlparse
import requests
from .brands import SHORTENERS
from .lexical import normalized
from .schema import Hop

UA={"User-Agent":"QRShield-Analyzer/1.0"}; BLOCKED={"file","ftp","javascript","data"}
def _safe_host(hostname: str) -> None:
    if not hostname: raise ValueError("URL has no hostname")
    for item in socket.getaddrinfo(hostname,None):
        ip=ipaddress.ip_address(item[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified: raise ValueError("private or reserved network address blocked")
def _meta_redirect(text: str) -> str|None:
    import re
    match=re.search(r"(?:url\s*=|(?:window\.)?location(?:\.href)?\s*=)\s*['\"]?([^'\" >;]+)",text,re.I); return match.group(1) if match else None
@lru_cache(maxsize=256)
def resolve(raw: str) -> tuple[list[Hop],str,str,list[str]]:
    url=normalized(raw); parsed=urlparse(url)
    if parsed.scheme in BLOCKED or parsed.scheme not in {"http","https"}: raise ValueError("only HTTP and HTTPS links can be checked")
    hops=[]; findings=[]; started=time.monotonic(); session=requests.Session(); session.cookies.clear()
    for index in range(8):
        if time.monotonic()-started>7: findings.append("Analysis timed out"); break
        parsed=urlparse(url); _safe_host(parsed.hostname or ""); kind="shortener" if (parsed.hostname or "").lower() in SHORTENERS else "start" if index==0 else "redirect"
        try: response=session.get(url,headers=UA,allow_redirects=False,timeout=4,stream=True,verify=True)
        except requests.exceptions.SSLError:
            findings.append("SSL certificate could not be verified"); response=session.get(url,headers=UA,allow_redirects=False,timeout=4,stream=True,verify=False)
        except requests.RequestException as exc: findings.append(f"Network request failed: {exc.__class__.__name__}"); hops.append(Hop(url,parsed.hostname or "",0,kind,"Request failed")); break
        hops.append(Hop(url,parsed.hostname or "",response.status_code,kind,""))
        location=response.headers.get("Location")
        if location and response.is_redirect: url=urljoin(url,location); continue
        content_type=response.headers.get("Content-Type","").lower(); disp=response.headers.get("Content-Disposition","").lower(); ext=parsed.path.lower().split("?")[0]
        if "attachment" in disp or ext.endswith((".apk",".exe",".scr",".msi",".zip")): findings.append("Download trigger detected")
        text=""
        if "text/html" in content_type:
            content=b"".join(chunk for chunk in response.iter_content(16384) if len(chunk)<=300000)[:300000]; text=content.decode(response.encoding or "utf-8",errors="ignore")
            next_url=_meta_redirect(text)
            if next_url:
                findings.append("Meta or JavaScript redirect detected"); hops[-1].note="Meta/JS redirect"; url=urljoin(url,next_url); continue
        hops[-1].kind="final"; return hops,text,url,findings
    return hops,"",url,findings
