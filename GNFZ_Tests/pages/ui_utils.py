import os
import time

def wait_for_page_stable(page, timeout=30000):
    """Wait for network and DOM to be stable. Handles slow environments gracefully."""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception as e:
        print(f"Warning: Page stability wait timeout or error: {e}")

def close_blocking_modals(page):
    """Detect and close global blocking modals (e.g. #ng-modal-generic)."""
    try:
        # Check if backdrop or modal is present and visible
        blocking_elements = page.locator(".modal-backdrop.show, .modal.show, #ng-modal-generic")
        if blocking_elements.count() > 0 and blocking_elements.first.is_visible():
            print("Blocking modal detected. Attempting to close...")
            # Try to find a close button in any active modal
            close_btn = page.locator(".modal.show .btn-close, .modal.show #modal-generic-close, .modal.show .close, #ng-modal-generic .btn-close").first
            if close_btn.count() > 0 and close_btn.is_visible():
                try:
                    close_btn.click(force=True, timeout=2000)
                except:
                    close_btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
            else:
                # If no close button, try Escape key
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
            
            # Wait for backdrop to disappear
            backdrop = page.locator(".modal-backdrop.show")
            if backdrop.count() > 0:
                try:
                    backdrop.first.wait_for(state="hidden", timeout=3000)
                except:
                    pass
    except Exception as e:
        print(f"Error handling blocking modals: {e}")

def take_screenshot(page, name_prefix):
    """Capture a screenshot for debugging."""
    try:
        os.makedirs("test_output/screenshots", exist_ok=True)
        filename = f"test_output/screenshots/{name_prefix}_{int(time.time())}.png"
        page.screenshot(path=filename)
        print(f"Screenshot saved to {filename}")
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")

def sc(locator):
    """Scroll element into center view safely."""
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
    except:
        pass

def safe_click(page, locator, force=False, timeout=10000, wait_after=500):
    """
    Robust click that handles interception by closing modals and retrying.
    This replaces naive .click() and evaluate("el.click()").
    """
    try:
        locator.first.wait_for(state="attached", timeout=timeout)
        sc(locator.first)
        page.wait_for_timeout(200)
    except Exception:
        pass # Ignore visibility/scroll errors and try anyway

    try:
        # First attempt native click
        locator.first.click(force=force, timeout=3000)
        if wait_after:
            page.wait_for_timeout(wait_after)
    except Exception as e:
        err_str = str(e).lower()
        if "intercept" in err_str or "timeout" in err_str:
            print(f"Click intercepted or timeout. Clearing modals... ({e})")
            close_blocking_modals(page)
            # Second attempt
            try:
                locator.first.click(force=force, timeout=5000)
                if wait_after:
                    page.wait_for_timeout(wait_after)
            except Exception as e2:
                print(f"Retry click failed, forcing with JS... ({e2})")
                try:
                    locator.first.evaluate("el => el.click()")
                    if wait_after:
                        page.wait_for_timeout(wait_after)
                except Exception as e3:
                    print(f"Total click failure: {e3}")
                    take_screenshot(page, "click_failure")
                    raise e3
        else:
            raise e
