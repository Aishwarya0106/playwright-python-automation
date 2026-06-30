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
    """Detect and close/remove global blocking modals (e.g. #ng-modal-generic) to prevent click interception."""
    try:
        # 1. Look for known modals
        modals = page.locator(".modal.show, #ng-modal-generic, .modal-backdrop.show")
        count = modals.count()
        if count > 0 and modals.first.is_visible():
            print("  [MODAL] Blocking modal or backdrop detected.")
            # Try to click close button
            close_btn = page.locator(".modal.show .btn-close, .modal.show [data-bs-dismiss='modal'], #ng-modal-generic .btn-close, #ng-modal-generic button:has-text('Close')").first
            if close_btn.count() > 0 and close_btn.is_visible():
                print("  [MODAL] Clicking close button...")
                try:
                    close_btn.click(force=True, timeout=2000)
                except:
                    close_btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
            else:
                # Try Escape key
                print("  [MODAL] Pressing Escape...")
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)

        # 2. Force remove from DOM if still visible/blocking (nuclear option for stubborn overlays)
        page.evaluate("""
            (function() {
                var items = document.querySelectorAll('.modal.show, .modal-backdrop, #ng-modal-generic');
                if (items.length > 0) {
                    console.log('Force removing ' + items.length + ' blocking modal elements from DOM');
                    for (var i = 0; i < items.length; i++) {
                        items[i].remove();
                    }
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                }
            })()
        """)
        page.wait_for_timeout(300)
    except Exception as e:
        print(f"Warning in close_blocking_modals: {e}")

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

def safe_click(page, locator, force=False, timeout=10000, wait_after=500, max_retries=3):
    """
    Highly robust click helper for Playwright + Python.
    - Waits for the element to be attached, visible, stable, and enabled.
    - Dismisses blocking loaders and spinners.
    - Detects and closes/removes blocking modals (like #ng-modal-generic).
    - Scrolls element into view centered.
    - Retries native clicks multiple times with dynamic delay.
    - Falls back to JS click only if native click fails.
    - Captures screenshots and dumps DOM state on final failure.
    """
    # 1. Wait for page load state & spinners
    wait_for_page_stable(page, timeout=timeout)
    
    target = locator.first
    selector_str = str(locator)
    
    # 2. Wait for element state
    try:
        target.wait_for(state="attached", timeout=timeout)
    except Exception as e:
        print(f"  [safe_click] Error: Element not attached to DOM: {selector_str}")
        take_screenshot(page, "click_not_attached")
        raise e

    # Close any pre-existing blocking modals
    close_blocking_modals(page)
    
    # Scroll into view
    sc(target)
    page.wait_for_timeout(200)

    # 3. Retry Loop for Click
    for attempt in range(1, max_retries + 1):
        try:
            # Check visibility and enabled status
            if not target.is_visible():
                print(f"  [safe_click] Element not visible, waiting... (Attempt {attempt}/{max_retries})")
                target.wait_for(state="visible", timeout=3000)
            
            # Wait for element to be stable & enabled
            target.click(force=force, timeout=3000)
            
            # Click succeeded!
            if wait_after:
                page.wait_for_timeout(wait_after)
            return
            
        except Exception as e:
            err_msg = str(e)
            print(f"  [safe_click] Attempt {attempt} failed: {err_msg}")
            
            # If intercepted by modal/overlay
            if "intercept" in err_msg.lower() or "visible" in err_msg.lower() or "stable" in err_msg.lower():
                print("  [safe_click] Click intercepted or element unstable. Handling modals & retrying...")
                close_blocking_modals(page)
                wait_for_page_stable(page, timeout=5000)
                sc(target)
                page.wait_for_timeout(300)
            else:
                page.wait_for_timeout(500)

    # 4. Fallback to JS Click
    print("  [safe_click] Native click failed after retries. Attempting JS click fallback...")
    try:
        target.evaluate("el => el.click()")
        if wait_after:
            page.wait_for_timeout(wait_after)
        print("  [safe_click] JS click succeeded.")
        return
    except Exception as js_err:
        print(f"  [safe_click] JS click also failed: {js_err}")
        take_screenshot(page, "click_final_failure")
        try:
            html_dump = page.content()
            dump_path = f"test_output/screenshots/failure_dom_{int(time.time())}.html"
            os.makedirs("test_output/screenshots", exist_ok=True)
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(html_dump)
            print(f"  [safe_click] DOM dump saved to {dump_path}")
        except:
            pass
        raise js_err

