# app.py — LYRA Root Launcher
# ─────────────────────────────────────────────────────────────────────────────
# Always run from project root:
#   python -m streamlit run app.py
#
# This file exists purely to fix Windows Streamlit multi-page detection.
# Streamlit finds pages/ relative to the file passed to streamlit run.
# By putting app.py at the root, pages/ sits right next to it and
# Streamlit registers all pages correctly.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

# Ensure project root is on path so all src.* imports work correctly
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Run the main app by executing streamlit_app.py in the current scope.
# This is equivalent to running streamlit_app.py directly but from root level,
# which allows Streamlit to correctly detect the pages/ folder next to app.py.
_app_path = os.path.join(ROOT, "src", "ui", "streamlit_app.py")
with open(_app_path, encoding="utf-8") as _f:
    exec(_f.read(), {"__file__": _app_path})