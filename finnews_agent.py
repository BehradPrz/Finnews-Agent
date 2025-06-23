"""
Financial News Tracker - Main Entry Point
=========================================

Production-ready Streamlit application for financial news analysis.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui import main

if __name__ == "__main__":
    main()
