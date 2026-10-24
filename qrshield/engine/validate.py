from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def metrics() -> dict:
    path=ROOT/"models"/"metrics.json"
    if path.exists(): return json.loads(path.read_text())
    return {"precision":0.0,"recall":0.0,"f1":0.0,"accuracy":0.0,"matrix":[[0,0],[0,0]],"n_train":0,"n_test":0,"provenance":"Model not trained yet; lexical safety rules remain active."}
