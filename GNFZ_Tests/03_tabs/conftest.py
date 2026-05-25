import sys
import os

# Walk up: 03_tabs/ → GNFZ_Tests/ → GNFZ_AUTOMATION (root)
root       = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gnfz_tests = os.path.join(root, "GNFZ_Tests")

for p in [root, gnfz_tests]:
    if p not in sys.path:
        sys.path.insert(0, p)