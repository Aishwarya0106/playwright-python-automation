import sys
import os
import shared_browser as sb
from playwright.sync_api import sync_playwright

# Add GNFZ_Tests folder to sys.path
# report_utils.py and shared_browser.py live here
# This makes them importable from any subfolder test file
gnfz_tests = os.path.dirname(os.path.abspath(__file__))
if gnfz_tests not in sys.path:
    sys.path.insert(0, gnfz_tests)


def start_shared_browser():
    if getattr(sb, "pw", None) is None:
        sb.pw = sync_playwright().start()
    if getattr(sb, "browser", None) is None:
        sb.browser = sb.pw.chromium.launch(
            headless=False,
            slow_mo=800,
            args=["--start-maximized"]
        )
    if getattr(sb, "context", None) is None:
        sb.context = sb.browser.new_context(no_viewport=True)
    if getattr(sb, "page", None) is None:
        sb.page = sb.context.new_page()
        print("\n[+] Shared browser session started.")


def close_shared_browser():
    try:
        if getattr(sb, "page", None):
            sb.page.close()
        if getattr(sb, "context", None):
            sb.context.close()
        if getattr(sb, "browser", None):
            sb.browser.close()
        if getattr(sb, "pw", None):
            sb.pw.stop()
    except Exception:
        pass
    finally:
        sb.page = None
        sb.context = None
        sb.browser = None
        sb.pw = None


def pytest_sessionstart(session):
    start_shared_browser()


def pytest_sessionfinish(session, exitstatus):
    try:
        import report_utils as ru
        ru.write_report()
    except Exception as e:
        print(f"Failed to write report: {e}")
    close_shared_browser()