from __future__ import annotations
from .store import load_policy, save_policy
DEFAULT = {"medium_from":30,"high_from":65,"block_shorteners":False,"flag_open_wifi":True,"lookalike_detection":True,"page_inspection":True,"payload_checks":True,"allowlist":["hdfcbank.com","github.com"],"blocklist":["hdfc-kyc-update.top"]}
def get_policy() -> dict: return load_policy(DEFAULT)
def set_policy(data: dict) -> None: save_policy(data)
