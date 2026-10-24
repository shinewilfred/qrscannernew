from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib,pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,f1_score,precision_score,recall_score
from sklearn.model_selection import train_test_split
from engine.lexical import features
from engine.ml import FEATURES
def main():
    data=ROOT/"data"/"labeled_urls.csv"
    if not data.exists(): from build_dataset import main as build; build()
    frame=pd.read_csv(data); x=[[features(url)[key] for key in FEATURES] for url in frame.url]; train_x,test_x,train_y,test_y=train_test_split(x,frame.label,stratify=frame.label,test_size=.2,random_state=2026)
    model=RandomForestClassifier(n_estimators=200,class_weight="balanced",random_state=2026).fit(train_x,train_y); predicted=model.predict(test_x); (ROOT/"models").mkdir(exist_ok=True); joblib.dump(model,ROOT/"models"/"url_model.joblib")
    provenance=json.loads((ROOT/"data"/"provenance.json").read_text()); synthetic=sum(value for value in provenance.values() if isinstance(value,int)); metrics={"precision":precision_score(test_y,predicted),"recall":recall_score(test_y,predicted),"f1":f1_score(test_y,predicted),"accuracy":accuracy_score(test_y,predicted),"matrix":confusion_matrix(test_y,predicted).tolist(),"n_train":len(train_y),"n_test":len(test_y),"provenance":f"Prototype dataset, {len(frame)} samples, includes {synthetic} synthetic URLs."}; (ROOT/"models"/"metrics.json").write_text(json.dumps(metrics,indent=2)); print(metrics)
if __name__=="__main__": main()
