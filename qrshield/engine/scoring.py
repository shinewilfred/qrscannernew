from __future__ import annotations
import ipaddress
from urllib.parse import urlparse
from rapidfuzz.fuzz import ratio
from .brands import BRANDS,RISKY_TLDS,SHORTENERS
from .lexical import entropy,host,registered_domain
from .schema import Reason

def trusted_domain(domain: str) -> bool:
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/"data"/"trusted_domains.txt"
    return domain in set(path.read_text().splitlines()) if path.exists() else False

def lexical_reasons(url: str) -> list[Reason]:
    parsed=urlparse(url); hostname=host(url); reasons=[]
    try: ipaddress.ip_address(hostname); reasons.append(Reason("IP address destination","The link uses an IP address instead of a domain.","danger",25))
    except ValueError: pass
    if "xn--" in hostname or any(ord(char)>127 for char in hostname): reasons.append(Reason("Lookalike characters","The address uses punycode or mixed-script characters.","danger",25))
    labels=hostname.split("."); registered=registered_domain(url)
    for brand,official in BRANDS.items():
        suspicious=brand in labels[:-2] and registered not in official or any(0 < len(part) and 100-ratio(brand,part)<=2 for part in labels)
        if suspicious: reasons.append(Reason("Brand lookalike",f"{brand.title()} appears in an unofficial address.","danger",30)); break
    if hostname.rsplit(".",1)[-1] in RISKY_TLDS: reasons.append(Reason("Risky domain ending","This TLD is frequently used in phishing.","warn",12))
    if len(labels)>=4: reasons.append(Reason("Deep subdomain","This address has many subdomains.","warn",10))
    if len(url)>100: reasons.append(Reason("Very long link","Long links can hide the real destination.","warn",6))
    if "@" in url: reasons.append(Reason("Misleading @ symbol","Text before @ is not the destination.","danger",15))
    if hostname.count("-")>=3: reasons.append(Reason("Many hyphens","The hostname is unusually complex.","warn",8))
    if entropy(hostname)>3.7: reasons.append(Reason("Random-looking hostname","The address has unusually high character randomness.","warn",8))
    if parsed.scheme!="https": reasons.append(Reason("Not HTTPS","This link is not encrypted.","warn",10))
    if parsed.port and parsed.port not in (80,443): reasons.append(Reason("Non-standard port","The link uses an unusual network port.","warn",8))
    if hostname in SHORTENERS: reasons.append(Reason("Shortened link","The destination is hidden behind a short link.","warn",7))
    if not trusted_domain(registered) and any(word in url.lower() for word in ["login","verify","update","secure","kyc","wallet","otp"]): reasons.append(Reason("Sensitive wording","The link uses sign-in or verification wording.","warn",8))
    return reasons
def payload_reasons(kind: str,payload: dict) -> list[Reason]:
    if kind=="qr_upi":
        reasons=[Reason("UPI safety note","Scanning a UPI QR only SENDS money. It never receives money.","info",0)]; payee=(payload.get("Payee name") or "").lower(); vpa=(payload.get("VPA") or "").lower(); note=(payload.get("Note") or "").lower()
        if any(word in payee for word in ["amazon","refund","support"]) and not any(word in vpa for word in ["amazon","support"]): reasons.append(Reason("Payee mismatch","The named payee does not match the personal-looking VPA.","danger",30))
        if payload.get("Amount") not in ("","Not set"): reasons.append(Reason("Prefilled amount","This QR is ready to send money.","warn",15))
        if any(word in note for word in ["refund","cashback","prize","reward","kyc","lottery"]): reasons.append(Reason("Payment lure","The note uses a common scam lure.","danger",20))
        if vpa and not vpa.endswith(("@okhdfcbank","@oksbi","@okicici","@paytm")): reasons.append(Reason("Unknown payment handle","The VPA uses an unfamiliar PSP handle.","warn",10))
        return reasons
    if kind=="qr_wifi":
        security=(payload.get("Security") or "").lower(); ssid=(payload.get("Network") or "").lower(); result=[]
        if security in {"nopass",""}: result.append(Reason("Open network","This Wi‑Fi network has no password.","warn",25))
        if security=="wep": result.append(Reason("Weak WEP security","WEP can be broken easily.","warn",15))
        if "free" in ssid or "wifi" in ssid: result.append(Reason("Generic network name","The network name resembles a public Wi‑Fi lure.","warn",15))
        return result
    return []
def final_score(reasons: list[Reason], ml: float, policy: dict, url: str="") -> tuple[int,str,float]:
    rule=min(100,sum(max(0,item.points) for item in reasons)); score=round(.65*rule+.35*ml*100)
    hostname=host(url) if url else ""
    from pathlib import Path
    local=(Path(__file__).resolve().parents[1]/"data"/"blocklist.txt")
    blocked=set(policy.get("blocklist",[])) | (set(local.read_text().splitlines()) if local.exists() else set())
    if hostname in blocked: reasons.append(Reason("Local blocklist match","This destination is on the local blocklist.","danger",100)); score=100
    domain=registered_domain(url) if url else ""
    if domain in policy.get("allowlist",[]) or trusted_domain(domain):
        severe={"Lookalike characters","Brand lookalike","Local blocklist match"}
        if not any(item.title in severe for item in reasons):
            score=min(score,10); reasons.append(Reason("Trusted official domain","This registered domain is in the bundled trusted-domain set.","safe",-10))
    level="High" if score>=policy["high_from"] else "Medium" if score>=policy["medium_from"] else "Low"
    confidence=min(.99,.55+abs(rule-ml*100)/200+min(4,sum(item.points>=15 for item in reasons))*.07)
    if level=="Low": reasons.append(Reason("No strong danger signals","No high-risk pattern was found in this analysis.","safe",-3))
    return score,level,confidence
