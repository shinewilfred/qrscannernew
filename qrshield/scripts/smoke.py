import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import analyze
CASES=[("https://hdfcbank.com/personal","Low"),("https://bit.ly/3xYz-KYC","High"),("upi://pay?pa=refund.desk@oksbi&pn=Amazon Refund&am=4999&tn=Cashback","High"),("WIFI:T:nopass;S:Free_Airport_WiFi;;","Medium"),("https://github.com/streamlit/streamlit","Low"),("https://login.microsoftonline.com.secure-auth.xyz","High"),("smsto:+919999999999:Your parcel is held, pay fee http://short.ly/xx","Medium"),("http://127.0.0.1/admin","Medium"),("https://xn--paypa1-9za.top/login","Medium"),("just ordinary text","Low")]
for raw,expected in CASES:
    result=analyze(raw); print(f"{result.level:6} {result.score:3} {raw[:48]}"); assert result.level==expected,(raw,result.level,expected)
