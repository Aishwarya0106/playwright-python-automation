# browser_manager.py
# Shared browser instance used by both test_sign_up.py and test_sign_in.py

from playwright.sync_api import sync_playwright

pw      = None
browser = None
context = None
page    = None


def start_browser():
    global pw, browser, context, page
    pw      = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=False,
        slow_mo=800,
        args=["--start-maximized"]
    )
    context = browser.new_context(no_viewport=True)
    page    = context.new_page()
    print("\n🚀 Browser launched.")


def close_browser():
    global pw, browser, context, page
    try:
        if page:    page.close()
        if context: context.close()
        if browser: browser.close()
        if pw:      pw.stop()
        print("\n🔒 Browser closed.")
    except Exception:
        pass
    finally:
        page    = None
        context = None
        browser = None
        pw      = None


def get_page():
    return page