#!/usr/bin/env python3
"""
Test Chrome version detection from registry
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the function
from scraper import get_chrome_version_from_registry

# Test it
print("Testing Chrome version detection...")
print("=" * 60)

version = get_chrome_version_from_registry()

if version:
    print(f"[OK] Chrome version detected: {version}")
else:
    print("[INFO] Could not detect Chrome version")
    print("       This is OK - the script will use auto-detection")

print("=" * 60)
