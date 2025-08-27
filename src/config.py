from __future__ import annotations
from pathlib import Path

# Base project directory (assumes this file stays in src/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
# Primary expected location
RAW_DATA_FILE = DATA_DIR / "yks_tablo.csv"
# Fallback (original location) if not yet moved
LEGACY_RAW_DATA_FILE = BASE_DIR / "yks_tablo.csv"

# Add future configurable constants here
