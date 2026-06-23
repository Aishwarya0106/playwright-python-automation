import shared_browser as sb
from pages import ui_utils as uu

class OverviewPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.overview_tab = self.page.locator("label[for='tab1'], li#gnfz-overview label, li#gnfz-overview").first
        
        # Selectors inside overview
        self.building_info_select = self.page.locator("select#gnfz-building-info, select[id*='building-info'], select#gnfz-asset-info, select[id*='asset-info'], select#gnfz-basic-info, select[id*='basic-info']").first
        self.team_info_select = self.page.locator("select#gnfz-team-info, select[id*='team-info']").first
        self.complete_assessment_select = self.page.locator("select#gnfz-complete-assessment, select[id*='complete-assessment']").first
        self.net_zero_plans_select = self.page.locator("select#gnfz-nzp, select[id*='nzp']").first
        self.error_message = self.page.locator("small.text-danger, .text-danger, .invalid-feedback, .alert-danger, .swal2-html-container, .swal2-title, .toast-body, #error-message").first

    def navigate_to_overview(self):
        print("Navigating to Overview tab...")
        uu.wait_for_page_stable(self.page)
        
        # Helper to check if Overview tab is active
        def is_overview_active():
            try:
                inp = self.page.locator("input#tab1, #tab1").first
                if inp.count() > 0 and inp.is_checked():
                    return True
            except Exception:
                pass
            return self.building_info_select.count() > 0 and self.building_info_select.is_visible()

        if is_overview_active():
            print("  Overview tab is already active.")
            return

        # Method 1: safe_click on the tab element
        try:
            print("  Method 1: Click overview_tab natively...")
            uu.safe_click(self.page, self.overview_tab, wait_after=1000)
        except Exception as e:
            print(f"  Method 1 failed: {e}")

        # Method 2: Check radio input via JS directly (this works for CSS-only tabs)
        if not is_overview_active():
            try:
                print("  Method 2: Checking radio button #tab1 via JS...")
                self.page.evaluate("""
                    (function() {
                        var el = document.getElementById('tab1') || document.querySelector('input#tab1') || document.querySelector('input[id*="tab1"]');
                        if (el) {
                            el.checked = true;
                            el.click();
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            el.dispatchEvent(new Event('click', {bubbles: true}));
                            return true;
                        }
                        return false;
                    })()
                """)
                self.page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Method 2 warning: {e}")

        # Method 3: Click label via JS directly
        if not is_overview_active():
            try:
                print("  Method 3: Clicking label[for='tab1'] via JS...")
                self.page.evaluate("""
                    (function() {
                        var el = document.querySelector('label[for="tab1"]') || document.querySelector('li#gnfz-overview label') || document.querySelector('#gnfz-overview label');
                        if (el) {
                            el.click();
                            el.dispatchEvent(new Event('click', {bubbles: true}));
                            return true;
                        }
                        return false;
                    })()
                """)
                self.page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Method 3 warning: {e}")

        # Method 4: Native check on input
        if not is_overview_active():
            try:
                print("  Method 4: Checking input#tab1 natively...")
                inp = self.page.locator("input#tab1, #tab1").first
                if inp.count() > 0:
                    inp.check(force=True, timeout=5000)
                    self.page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  Method 4 warning: {e}")

        # Method 5: Native click on alternative selectors
        if not is_overview_active():
            print("  Method 5: Native clicks on alternative selectors...")
            selectors = [
                "label[for='tab1']",
                "li#gnfz-overview label",
                "li#gnfz-overview",
                "#gnfz-overview"
            ]
            for sel in selectors:
                loc = self.page.locator(sel).first
                if loc.count() > 0:
                    try:
                        loc.scroll_into_view_if_needed(timeout=2000)
                        loc.click(force=True, timeout=5000)
                        self.page.wait_for_timeout(2000)
                        if is_overview_active():
                            print(f"    [SUCCESS] Activated using native click on '{sel}'")
                            break
                    except Exception as e:
                        print(f"    Native click failed on '{sel}': {e}")

        if is_overview_active():
            print("  [PASS] Overview tab successfully activated.")
        else:
            print("  [WARNING] Overview tab did not report as active. Taking screenshot...")
            uu.take_screenshot(self.page, "overview_navigation_failed")

    def are_all_fields_visible(self):
        try:
            checks = [
                ("Building Info/Asset Info/Basic Info", self.building_info_select),
                ("Team Info", self.team_info_select),
                ("Complete Assessment", self.complete_assessment_select),
                ("Net Zero Plans", self.net_zero_plans_select),
            ]

            for labels_str, locator in checks:
                # Primary check: select element present and visible
                if locator.count() > 0 and locator.is_visible():
                    continue

                # Fallback: look for any label/text indicating the field is present
                labels = [l.strip() for l in labels_str.split("/")]
                found_label = False
                for label in labels:
                    alt = self.page.locator(f".text-label:has-text('{label}'), label:has-text('{label}'), .form-label:has-text('{label}'), text=\"{label}\"")
                    if alt.count() > 0 and alt.first.is_visible():
                        found_label = True
                        break
                if found_label:
                    continue

                # If neither primary nor fallback found, fail
                raise AssertionError(f"Overview field '{labels_str}' not found or not visible")

            return True
        except Exception as e:
            print(f"Error: Overview field check failed: {e}")
            return False

    def submit_assessment_for_review(self):
        uu.sc(self.complete_assessment_select)
        self.complete_assessment_select.select_option(label="Submit for review")
        self.page.wait_for_timeout(1000)
        
        # Click YES on the confirmation popup if it appears
        yes_btn = self.page.locator("button#simple-process-status-submit-change-event-popup, button:has-text('YES')").first
        try:
            if yes_btn.count() > 0:
                yes_btn.wait_for(state="visible", timeout=3000)
                uu.safe_click(self.page, yes_btn, wait_after=2000)
        except Exception as e:
            print(f"  Warning: Click YES on confirmation failed: {e}")
            
        uu.wait_for_page_stable(self.page)
        self.page.wait_for_timeout(1000)

    def get_error_message(self):
        try:
            self.error_message.wait_for(state="visible", timeout=10000)
            return self.error_message.inner_text().strip()
        except Exception:
            return ""

    def change_status_and_confirm(self, select_locator, status_label):
        """Select a status from a dropdown, click YES on confirmation popup, and wait for update."""
        uu.sc(select_locator)
        # Select the option
        select_locator.select_option(label=status_label)
        self.page.wait_for_timeout(1000)
        
        # Look for the confirmation YES button
        yes_btn = self.page.locator("button#simple-process-status-submit-change-event-popup, button:has-text('YES')").first
        yes_btn.wait_for(state="visible", timeout=5000)
        uu.safe_click(self.page, yes_btn, wait_after=2000)
        
        # Wait for loaders and page stability
        uu.wait_for_page_stable(self.page)
        self.page.wait_for_timeout(1000)

    def get_selected_status(self, select_locator):
        """Get the text of the currently selected option."""
        return select_locator.evaluate("el => el.options[el.selectedIndex].text").strip()
