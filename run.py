#!/usr/bin/env python3
"""
run.py

Main entry point for New Zealand LSAP Bond Sales Data Scraper
Run this file from the project root directory
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator import main

if __name__ == '__main__':
    sys.exit(main())
