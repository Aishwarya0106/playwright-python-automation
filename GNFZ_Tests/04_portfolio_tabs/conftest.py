import sys
import os

# Walk up: 04_portfolio_tabs/ → GNFZ_Tests/ → GNFZ_AUTOMATION (root)
root       = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
gnfz_tests = os.path.join(root, "GNFZ_Tests")

for p in [root, gnfz_tests]:
    if p not in sys.path:
        sys.path.insert(0, p)

def pytest_runtest_setup(item):
    import shared_browser as sb
    project_type = getattr(sb, "project_type", "building")
    if project_type != "portfolio":
        import pytest
        pytest.skip(f"Skipping portfolio testcase '{item.name}' because active project type is '{project_type}'")
