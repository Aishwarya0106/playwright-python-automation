import sys
import os

# Add GNFZ_AUTOMATION root to sys.path
# This makes shared_browser.py and report_utils.py importable everywhere
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

# Ensure GNFZ_Tests is also on path for imports
gnfz_tests = os.path.join(root, "GNFZ_Tests")
if gnfz_tests not in sys.path:
    sys.path.insert(0, gnfz_tests)


def pytest_addoption(parser):
    parser.addoption(
        "--type",
        action="store",
        default="building",
        help="Project type to run: building or portfolio"
    )


def pytest_configure(config):
    import shared_browser as sb
    sb.project_type = config.getoption("--type").lower()
    print(f"\n[+] Configured GNFZ test suite for project type: '{sb.project_type}'")