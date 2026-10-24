from __future__ import annotations
from bs4 import BeautifulSoup
from .lexical import registered_domain
from .schema import Reason
def inspect(html: str, url: str) -> tuple[list[Reason],list[str],str]:
    if not html: return [],[],""
    soup=BeautifulSoup(html,"html.parser"); text=soup.get_text(" ",strip=True).lower(); findings=[]; reasons=[]; title=soup.title.get_text(" ",strip=True) if soup.title else ""
    if soup.select('input[type="password"]'): reasons.append(Reason("Password field","This page asks for a password.","danger",18)); findings.append("Password field")
    for form in soup.find_all("form"):
        action=form.get("action","")
        if action and registered_domain(action) and registered_domain(action)!=registered_domain(url): reasons.append(Reason("Form posts elsewhere","The form submits to a different domain.","danger",15)); findings.append("Form posts to another domain"); break
    if any(phrase in text for phrase in ["account will be blocked","verify within 24 hours","act now"]): reasons.append(Reason("Urgency language","The page pressures you to act quickly.","warn",9)); findings.append("Urgency wording")
    if soup.select('iframe[hidden],iframe[style*="display:none"],iframe[width="0"]'): reasons.append(Reason("Hidden iframe","A hidden frame was found.","warn",10)); findings.append("Hidden iframe")
    if any(word in html.lower() for word in ["eval(","atob(","unescape("]): reasons.append(Reason("Obfuscated script","The source contains obfuscated JavaScript patterns.","warn",8)); findings.append("Obfuscated JavaScript")
    return reasons,findings,title
