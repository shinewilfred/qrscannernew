from __future__ import annotations
import json, sqlite3
from pathlib import Path
import pandas as pd
from .schema import ScanResult

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; DB=DATA/"qrshield.db"
def _conn() -> sqlite3.Connection:
    DATA.mkdir(exist_ok=True); conn=sqlite3.connect(DB); conn.execute("CREATE TABLE IF NOT EXISTS scans (id TEXT PRIMARY KEY, ts TEXT, type TEXT, raw TEXT, title TEXT, score INTEGER, level TEXT, confidence REAL, reasons TEXT, chain TEXT, payload TEXT, findings TEXT, actions TEXT, latency INTEGER, source TEXT)"); conn.execute("CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT)"); conn.execute("CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id TEXT, kind TEXT, ts TEXT)"); return conn
def save(result: ScanResult) -> None:
    with _conn() as conn: conn.execute("INSERT OR REPLACE INTO scans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(result.id,result.ts.isoformat(),result.input_type,result.raw,result.title,result.score,result.level,result.confidence,json.dumps([x.__dict__ for x in result.reasons]),json.dumps([x.__dict__ for x in result.chain]),json.dumps(result.payload),json.dumps(result.page_findings),json.dumps(result.actions),result.latency_ms,result.source))
def frame(limit: int=200, level: str|None=None, q: str|None=None, include_sample: bool=True) -> pd.DataFrame:
    sql="SELECT id,ts as Time,level as Level,score as Score,type as Type,title as Domain,raw as Raw,latency as 'Latency ms' FROM scans WHERE 1=1"; args=[]
    if not include_sample: sql+=" AND source != 'sample'"
    if level: sql+=" AND level=?"; args.append(level)
    if q: sql+=" AND raw LIKE ?"; args.append(f"%{q}%")
    sql+=" ORDER BY ts DESC LIMIT ?"; args.append(limit)
    return pd.read_sql_query(sql,_conn(),params=args)
def load_policy(default: dict) -> dict:
    with _conn() as conn: row=conn.execute("SELECT data FROM policy WHERE id=1").fetchone()
    return {**default,**(json.loads(row[0]) if row else {})}
def save_policy(data: dict) -> None:
    with _conn() as conn: conn.execute("INSERT OR REPLACE INTO policy VALUES(1,?)",(json.dumps(data),))
def feedback(scan_id: str, kind: str) -> None:
    from datetime import datetime
    with _conn() as conn: conn.execute("INSERT INTO feedback(scan_id,kind,ts) VALUES(?,?,?)",(scan_id,kind,datetime.now().isoformat()))
