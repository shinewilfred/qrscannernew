from __future__ import annotations
import math, re
from urllib.parse import urlparse
import tldextract

_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())

def normalized(value: str) -> str:
    value = value.strip().replace("hxxps://", "https://").replace("hxxp://", "http://").replace("[.]", ".").replace("(dot)", ".")
    return value if "://" in value else f"https://{value}"
def host(value: str) -> str: return (urlparse(normalized(value)).hostname or "").lower().rstrip(".")
def registered_domain(value: str) -> str:
    extracted = _EXTRACT(host(value))
    return ".".join(part for part in (extracted.domain, extracted.suffix) if part)
def entropy(text: str) -> float:
    return -sum((text.count(char)/len(text))*math.log2(text.count(char)/len(text)) for char in set(text)) if text else 0.0
def is_ip(value: str) -> bool:
    import ipaddress
    try: ipaddress.ip_address(host(value)); return True
    except ValueError: return False
def features(value: str) -> dict[str, float]:
    parsed=urlparse(normalized(value)); hostname=host(value); length=max(1,len(value))
    return {"length":len(value),"host_length":len(hostname),"dots":hostname.count("."),"hyphens":hostname.count("-"),"digits_ratio":sum(c.isdigit() for c in value)/length,"special_chars":sum(not c.isalnum() for c in value),"entropy":entropy(hostname),"subdomain_depth":max(0,len(hostname.split("."))-2),"has_ip":float(is_ip(value)),"has_punycode":float("xn--" in hostname),"risky_tld":float(hostname.rsplit(".",1)[-1] in __import__("engine.brands",fromlist=["RISKY_TLDS"]).RISKY_TLDS),"shortener":float(hostname in __import__("engine.brands",fromlist=["SHORTENERS"]).SHORTENERS),"keyword_count":sum(word in value.lower() for word in ["login","verify","update","secure","kyc","wallet","otp"]),"path_depth":len([p for p in parsed.path.split("/") if p]),"has_at":float("@" in value),"brand_distance":brand_distance(hostname)}
def brand_distance(hostname: str) -> float:
    from rapidfuzz.fuzz import ratio
    from .brands import BRANDS
    labels=BRANDS.keys(); return min(100-ratio(label, part) for label in labels for part in hostname.split("."))
def extract_urls(text: str) -> list[str]:
    matches=re.findall(r"(?:(?:https?|hxxps?)://|www\.)[^\s<>()\[\],;]+", text, re.I)
    return list(dict.fromkeys(normalized(item.rstrip(".,;:!?")) for item in matches))
