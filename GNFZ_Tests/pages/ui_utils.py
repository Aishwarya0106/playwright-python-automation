import os
import time

def wait_for_page_stable(page, timeout=30000):
    """Wait for network, DOM, and loading spinners/loaders to be stable."""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        # Use a shorter timeout for networkidle because Angular often has background polling
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception as e:
        print(f"Warning: Page stability wait timeout or error: {e}")

    # Wait for loaders/spinners to disappear to avoid click interception
    try:
        spinners = page.locator(".spinner-border, ngx-spinner, .loader, [class*='spinner'], [class*='loader']")
        count = spinners.count()
        for i in range(count):
            spinner = spinners.nth(i)
            if spinner.count() > 0 and spinner.is_visible():
                print(f"  [SPINNER] Waiting for visible loader/spinner to disappear...")
                spinner.wait_for(state="hidden", timeout=15000)
                # Wait briefly to let page stabilize after loader hides
                page.wait_for_timeout(500)
    except Exception as spinner_err:
        print(f"Warning waiting for spinners: {spinner_err}")

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

        # Fallback: forcefully remove modals/backdrops from DOM if they are still present
        remaining_modals = page.locator(".modal, .modal-backdrop, #ng-modal-generic")
        if remaining_modals.count() > 0:
            print("Forcefully removing remaining modals from DOM...")
            page.evaluate("""
                (function() {
                    var items = document.querySelectorAll('.modal, .modal-backdrop, #ng-modal-generic');
                    for (var i = 0; i < items.length; i++) {
                        items[i].remove();
                    }
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                })()
            """)
            page.wait_for_timeout(500)
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
    Robust click that handles interception by waiting for loaders, closing modals, and retrying.
    This replaces naive .click() and evaluate("el.click()").
    """
    # Wait for page stability and active loading spinners first
    wait_for_page_stable(page)

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
            print(f"Click intercepted or timeout. Clearing modals and re-waiting for loaders... ({e})")
            close_blocking_modals(page)
            # Re-wait for any loaders that might have appeared
            wait_for_page_stable(page)
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
