# QRShield: project rules
Product: QRShield, a pre-click link and QR analyzer for small firms with no security team (hackathon QUANTIX 2K26, PS07). Jury = industry professionals.
Priorities in order: (1) polished, animated, intuitive UI; (2) explainable results in plain language; (3) safety: a scanned URL is NEVER opened or rendered in a browser.

Stack: Python 3.11+, Streamlit (run `pip show streamlit` first; target >=1.40), SQLite, scikit-learn, requests, beautifulsoup4, opencv-python-headless, rapidfuzz, plotly, pandas, joblib. No paid APIs, no API keys.

Architecture: the ui/ package never imports requests, sklearn or cv2; it only calls the functions in engine/__init__.py. The single data contract is engine/schema.py. Phase 1 = mock engine. Phase 2 swaps in the real engine without changing any UI file except removing "sample" labels.

Working rules (save tokens):
- Read only files you need. Create each file in one pass. Do not refactor untouched files.
- No tests, README or docs, except a RUN.md of at most 10 lines (and scripts/smoke.py in Phase 2).
- Do not narrate. Final reply: at most 10 lines (files created, how to run, known gaps).
- Verify once: `python -m compileall -q .` then `streamlit run app.py --server.headless true` for about 8 seconds; confirm no traceback.

Code style: type hints, small functions, no dead code, no lorem ipsum, no external images, icons are inline SVG or emoji, fonts from Google Fonts with system fallbacks (venue Wi-Fi may fail).