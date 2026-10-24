from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; DATA.mkdir(exist_ok=True)
SAFE=["google.com","youtube.com","facebook.com","instagram.com","wikipedia.org","github.com","amazon.com","amazon.in","microsoft.com","apple.com","netflix.com","linkedin.com","reddit.com","whatsapp.com","hdfcbank.com","icicibank.com","sbi.co.in","streamlit.io","openai.com","stackoverflow.com"]
def main():
    rows=[]
    for index in range(15): rows.extend((f"https://{domain}/about/{index}",0,"synthetic-safe") for domain in SAFE)
    for brand in ["hdfc","microsoft","amazon","paypal","google"]:
        for word in ["login","verify","update","kyc","secure"]: rows.append((f"https://{brand}-{word}-account.top/{word}",1,"synthetic-phish")); rows.append((f"https://{brand}.secure-auth.xyz/{word}",1,"synthetic-phish"))
    with (DATA/"labeled_urls.csv").open("w",newline="") as output:
        writer=csv.writer(output); writer.writerow(["url","label","source"]); writer.writerows(rows)
    (DATA/"provenance.json").write_text(json.dumps({"synthetic_safe":len(SAFE)*15,"synthetic_phish":50,"openphish":0,"tranco":0,"network":"not requested by default; reproducible synthetic fallback used"},indent=2)); print(f"wrote {len(rows)} rows")
if __name__=="__main__": main()
