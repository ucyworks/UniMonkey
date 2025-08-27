"""
UniMonkey - YKS Yerleştirme Analizi Platformu
Streamlit Cloud deployment wrapper
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the main app
from ui.app import *
