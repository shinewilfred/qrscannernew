from __future__ import annotations
import html
from .schema import ScanResult
def html_report(result: ScanResult) -> str:
    reasons="".join(f"<li><b>{html.escape(item.title)}</b>: {html.escape(item.detail)} ({item.points:+d})</li>" for item in result.reasons); hops="".join(f"<li>{html.escape(item.domain)} · {item.status}</li>" for item in result.chain)
    return f"<!doctype html><meta charset=utf-8><title>QRShield report</title><body style='font-family:Arial;background:#070B14;color:#E6EDF7;padding:32px'><h1>🛡 QRShield</h1><h2>{result.level} risk · {result.score}/100</h2><p>{html.escape(result.raw)}</p><h3>Reasons</h3><ul>{reasons}</ul><h3>Journey</h3><ul>{hops}</ul><small>{result.ts.isoformat()} · never rendered</small></body>"
