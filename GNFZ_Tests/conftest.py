import sys
import os
import io

# Reconfigure stdout/stderr to use UTF-8 and avoid UnicodeEncodeError on Windows/Jenkins
if sys.platform.startswith("win"):
    for stream_name in ("stdout", "stderr", "__stdout__", "__stderr__"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

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
        slow_mo_val = int(os.environ.get("SLOW_MO", "800"))
        headless_val = os.environ.get("HEADLESS", "False").lower() == "true"
        sb.browser = sb.pw.chromium.launch(
            headless=headless_val,
            slow_mo=slow_mo_val,
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


import pytest

@pytest.fixture(autouse=True, scope="function")
def check_class_setup_status(request):
    """Check if class-level setup failed. If so, fail the test immediately to prevent cascading errors."""
    if request.cls and getattr(request.cls, "setup_error", None) is not None:
        pytest.fail(f"Class setup failed: {request.cls.setup_error}")


def pytest_collection_modifyitems(session, config, items):
    """Wrap setup_class method dynamically in a try-except block to capture setup errors without aborting pytest."""
    seen_classes = set()
    for item in items:
        cls = getattr(item, "cls", None)
        if cls and cls not in seen_classes:
            seen_classes.add(cls)
            setup_class_method = getattr(cls, "setup_class", None)
            if setup_class_method and not getattr(cls, "_setup_class_wrapped", False):
                original_setup = cls.setup_class
                
                @classmethod
                def make_wrapped_setup(orig):
                    def wrapped(wrapped_cls):
                        wrapped_cls.setup_error = None
                        try:
                            if hasattr(orig, "__func__"):
                                orig.__func__(wrapped_cls)
                            else:
                                orig(wrapped_cls)
                        except Exception as e:
                            wrapped_cls.setup_error = e
                            print(f"\n[SETUP CLASS FAILED] {wrapped_cls.__name__}: {e}")
                            try:
                                import shared_browser as sb
                                from pages import ui_utils as uu
                                uu.take_screenshot(sb.page, f"setup_failed_{wrapped_cls.__name__}")
                            except Exception as ex:
                                print(f"Failed to capture setup failure screenshot: {ex}")
                    return wrapped

                cls.setup_class = make_wrapped_setup(original_setup)
                cls._setup_class_wrapped = True