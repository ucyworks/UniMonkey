#!/usr/bin/env python3
"""
UniMonkey - YKS Yerleştirme Analizi Platformu
Main entry point for Streamlit Cloud deployment
"""

import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# UI dizinini de ekle
UI_DIR = PROJECT_ROOT / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

# Ana uygulamayı import et ve çalıştır
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Streamlit app'i çalıştır
    sys.argv = ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.headless=true"]
    sys.exit(stcli.main())
