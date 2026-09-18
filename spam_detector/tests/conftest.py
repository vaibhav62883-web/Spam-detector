"""
conftest.py
-----------
Adds spam_detector/ to sys.path so every test file can import
models, detector, advisor, history, etc. without relative-import gymnastics.
"""

import sys
import os

# Insert the spam_detector directory (parent of tests/) at the front of sys.path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
