import sys
import os

# Add GNFZ_AUTOMATION root to sys.path
# This makes shared_browser.py and report_utils.py importable everywhere
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)