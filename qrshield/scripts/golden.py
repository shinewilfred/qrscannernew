import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import analyze, get_policy

LEGIT=["https://www.google.com/search?q=python+tutorial&oq=python&sourceid=chrome","https://accounts.google.com/signin","https://www.youtube.com/watch?v=dQw4w9WgXcQ","https://github.com/streamlit/streamlit","https://www.microsoft.com/en-in","https://login.microsoftonline.com/common/oauth2/authorize","https://www.amazon.in/","https://www.flipkart.com/","https://www.irctc.co.in/nget/train-search","https://onlinesbi.sbi/","https://www.hdfcbank.com/personal","https://www.icicibank.com/","https://www.axisbank.com/","https://www.incometax.gov.in/","https://uidai.gov.in/","https://www.npci.org.in/","https://paytm.com/","https://phonepe.com/","https://en.wikipedia.org/wiki/Phishing","https://www.python.org/downloads/","https://streamlit.io/","https://www.who.int/","https://www.indiapost.gov.in/","https://www.nptel.ac.in/","https://web.whatsapp.com/","https://www.zoho.com/","https://www.bbc.com/news"]
BAD=["http://sbi-kyc-update.top/login","https://hdfcbank.com.verify-account.xyz/login","https://secure-icicibank-login.click/verify","http://paytm-refund.cfd/claim","https://amaz0n-in.top/gift","https://login.microsoftonline.com.secure-auth.xyz/common","https://xn--pypal-4ve.com/signin","https://irctc-ticket-refund.top/","https://uidai-aadhaar-update.xyz/","https://incometax-refund.click/","https://netflix-billing-help.icu/","http://203.0.113.45/login"]
failed=False
for expected, values in (("LEGIT",LEGIT),("BAD",BAD)):
    for value in values:
        result=analyze(value); print(f"{expected:5} {result.level:6} {result.score:3} | {', '.join(item.title for item in result.reasons[:3])}")
        bad=(expected=="LEGIT" and result.score>=get_policy()["medium_from"]) or (expected=="BAD" and result.level=="Low")
        failed |= bad
raise SystemExit(1 if failed else 0)
