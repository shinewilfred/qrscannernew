from __future__ import annotations
from pathlib import Path
import joblib
from .lexical import features
ROOT=Path(__file__).resolve().parents[1]; MODEL=ROOT/"models"/"url_model.joblib"
FEATURES=["length","host_length","dots","hyphens","digits_ratio","special_chars","entropy","subdomain_depth","has_ip","has_punycode","risky_tld","shortener","keyword_count","path_depth","has_at","brand_distance"]
def probability(url: str) -> float:
    if MODEL.exists():
        try: return float(joblib.load(MODEL).predict_proba([[features(url)[key] for key in FEATURES]])[0][1])
        except Exception: pass
    data=features(url); return min(.95,max(.03,(data["risky_tld"]*.25+data["has_ip"]*.28+data["shortener"]*.08+min(data["keyword_count"],3)*.1+data["has_punycode"]*.2)))
