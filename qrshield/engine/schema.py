from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reason:
    title: str; detail: str; severity: str; points: int


@dataclass
class Hop:
    url: str; domain: str; status: int; kind: str; note: str


@dataclass
class ScanResult:
    id: str; ts: datetime; input_type: str
    raw: str; title: str; score: int; level: str
    confidence: float; reasons: list[Reason]; chain: list[Hop]
    payload: dict; page_findings: list[str]; actions: list[str]
    latency_ms: int; source: str
