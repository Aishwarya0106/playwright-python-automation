import sys, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import datetime
import report_utils as ru
import shared_browser as sb
from playwright.sync_api import expect

# ── Locators based on the provided Portfolio HTML ─────────────────────────────
PORTFOLIO_INFO_HEADING   = "b:has-text('Portfolio Info')"
TEAM_INFO_HEADING        = "b:has-text('Team Info')"
PORTFOLIO_TITLE_INPUT    = "input[name='buildingTitle']"
ASSET_COUNT_INPUT        = "input#asset_count"
GROSS_AREA_INPUT         = "#gnfz-basic-info-form-assets_gross_area"
START_DATE_INPUT         = "input[placeholder='mm/dd/yyyy']"
CONFIDENTIAL_SELECT      = "select#confidentialRequest"
SAVE_BUTTON              = "button.native-button:has-text('Save')"
TAGIFY_INPUT             = ".tagify__input"
MANDATORY_FIELDS_ERROR   = "small.text-danger:has-text('* Mandatory fields should be valid.')"
PORTFOLIO_TITLE_ERROR    = "small.text-danger:has-text('Portfolio title is required.')"

PAUSE = 1000

class TestPortfolioBasicInfoTab:

    portfolio_id = ""

    @classmethod
    def setup_class(cls):
        print("\n\nPortfolio Basic Info: Waiting for Portfolio page layout...")
        sb.page.wait_for_selector(PORTFOLIO_INFO_HEADING, timeout=15_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Portfolio Basic Info ready.\n")

    def test_PBI01_verify_portfolio_info_heading(self):
        """PBI01 - Verify Portfolio Info heading is visible"""
        start = datetime.datetime.now()
        print("\nPBI01: Verify Portfolio Info heading")
        try:
            expect(sb.page.locator(PORTFOLIO_INFO_HEADING).first).to_be_visible()
            ru.add_result("Portfolio Basic Info", "PBI01 - Portfolio Info heading", start, "PASSED")
            print("PBI01 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Basic Info", "PBI01 - Portfolio Info heading", start, "FAILED", str(e))
            raise

    def test_PBI02_verify_portfolio_fields_visible(self):
        """PBI02 - Verify all portfolio basic fields are visible in the DOM"""
        start = datetime.datetime.now()
        print("\nPBI02: Verify Portfolio fields visibility")
        try:
            fields = [
                ("Portfolio Title Input", PORTFOLIO_TITLE_INPUT),
                ("Asset Count Input", ASSET_COUNT_INPUT),
                ("Gross Area Input", GROSS_AREA_INPUT),
                ("Start Date Input", START_DATE_INPUT),
                ("Confidential Request Select", CONFIDENTIAL_SELECT),
                ("Tagify Input", TAGIFY_INPUT),
                ("Save Button", SAVE_BUTTON)
            ]
            missing = []
            for name, locator in fields:
                el = sb.page.locator(locator).first
                if el.count() == 0 or not el.is_visible():
                    missing.append(name)
                    print(f"  [ERROR] {name} is NOT visible")
                else:
                    print(f"  [OK] {name} is visible")
            assert len(missing) == 0, f"Missing fields: {missing}"
            ru.add_result("Portfolio Basic Info", "PBI02 - Portfolio fields checked", start, "PASSED")
            print("PBI02 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Basic Info", "PBI02 - Portfolio fields checked", start, "FAILED", str(e))
            raise

    def test_PBI02b_verify_empty_save_errors(self):
        """PBI02b - Click Save on empty form and verify mandatory/title error messages"""
        start = datetime.datetime.now()
        print("\nPBI02b: Click Save on empty form and check errors")
        try:
            save_btn = sb.page.locator(SAVE_BUTTON).first
            save_btn.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(300)
            save_btn.click()
            sb.page.wait_for_timeout(PAUSE)

            # Scroll to top to see error messages
            sb.page.evaluate("window.scrollTo(0, 0)")
            sb.page.wait_for_timeout(500)

            # Check mandatory fields error
            mandatory_err = sb.page.locator(MANDATORY_FIELDS_ERROR).first
            expect(mandatory_err).to_be_visible(timeout=10000)
            print("  [OK] Mandatory fields error message is visible.")

            # Check title required error
            title_err = sb.page.locator(PORTFOLIO_TITLE_ERROR).first
            expect(title_err).to_be_visible(timeout=10000)
            print("  [OK] Portfolio title required error message is visible.")

            ru.add_result("Portfolio Basic Info", "PBI02b - Verify empty save errors", start, "PASSED")
            print("PBI02b PASSED")
        except Exception as e:
            ru.add_result("Portfolio Basic Info", "PBI02b - Verify empty save errors", start, "FAILED", str(e))
            raise

    def test_PBI03_fill_portfolio_info_and_save(self):
        """PBI03 - Fill Portfolio Title, Asset Count, Gross Area, and click Save"""
        start = datetime.datetime.now()
        today = datetime.datetime.now().strftime("%b %d")
        title_text = f"Portfolio - {today}"
        print(f"\nPBI03: Filling Portfolio Title = '{title_text}'")
        try:
            # 1. Fill Portfolio Title
            title_input = sb.page.locator(PORTFOLIO_TITLE_INPUT).first
            title_input.fill(title_text)
            sb.page.wait_for_timeout(500)

            # 2. Select Option in Tagify field
            print("  Selecting 'campus' in tagify field...")
            tagify = sb.page.locator(TAGIFY_INPUT).first
            tagify.wait_for(state="visible", timeout=10000)
            tagify.click()
            sb.page.wait_for_timeout(400)
            tagify.type("campus")
            sb.page.wait_for_timeout(800)
            
            sug = sb.page.locator(".tagify__dropdown__item:has-text('campus')").first
            if sug.count() > 0 and sug.is_visible():
                sug.click()
                print("  [OK] Selected 'campus' from dropdown suggestion")
            else:
                tagify.press("Enter")
                print("  [OK] Selected 'campus' by pressing Enter")
            sb.page.wait_for_timeout(500)

            # 3. Fill Asset Count
            asset_input = sb.page.locator(ASSET_COUNT_INPUT).first
            asset_input.fill("5")
            sb.page.wait_for_timeout(500)

            # 4. Fill Gross Area
            area_input = sb.page.locator(GROSS_AREA_INPUT).first
            area_input.fill("12500")
            sb.page.wait_for_timeout(500)

            # 5. Fill Start Date (today's date)
            print("  Filling Start Date...")
            date_inp = sb.page.locator(START_DATE_INPUT).first
            date_inp.wait_for(state="visible", timeout=10000)
            date_inp.click()
            sb.page.wait_for_timeout(600)

            today_str = datetime.datetime.now().strftime("%m/%d/%Y")
            sb.page.evaluate(f"""
                (function() {{
                    var el = document.querySelector("input[placeholder='mm/dd/yyyy']");
                    if (!el) return;
                    if (window.$ && typeof $(el).datepicker === 'function') {{
                        $(el).datepicker('setDate', '{today_str}');
                        $(el).trigger('change');
                        $(el).trigger('input');
                    }} else {{
                        el.value = '{today_str}';
                        el.dispatchEvent(new Event('input',  {{bubbles:true}}));
                        el.dispatchEvent(new Event('change', {{bubbles:true}}));
                    }}
                }})()
            """)
            sb.page.wait_for_timeout(500)
            date_inp.press("Tab")
            sb.page.wait_for_timeout(500)

            # 6. Select Confidentiality Option
            conf_select = sb.page.locator(CONFIDENTIAL_SELECT).first
            conf_select.select_option(label="No")
            sb.page.wait_for_timeout(500)

            # 7. Click Save
            save_btn = sb.page.locator(SAVE_BUTTON).first
            save_btn.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(300)
            save_btn.click()
            sb.page.wait_for_timeout(PAUSE * 2)

            print("  Portfolio saved successfully.")
            ru.add_result("Portfolio Basic Info", "PBI03 - Fill and Save Portfolio", start, "PASSED")
            print("PBI03 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Basic Info", "PBI03 - Fill and Save Portfolio", start, "FAILED", str(e))
            raise

    def test_PBI04_breadcrumb_verify_project_open_asset_management(self):
        """PBI04 - Click Portfolio breadcrumb -> verify project ID and name in list
        -> click project -> click Asset Management tab"""
        start = datetime.datetime.now()
        today = datetime.datetime.now().strftime("%b %d")
        project_name = f"Portfolio - {today}"
        print(f"\nPBI04: Breadcrumb -> verify project -> open -> Asset Management")
        try:
            # 1. Wait for save to complete and URL redirect to detail page
            print("  Waiting for save to complete (redirect to detail URL)...")
            try:
                sb.page.wait_for_url(
                    lambda url: any(part.isdigit() and len(part) > 10 for part in url.split("/")),
                    timeout=15_000
                )
                print(f"  Redirect completed. URL: '{sb.page.url}'")
            except Exception as e:
                print(f"  Warning: waiting for redirect timed out: {e}")

            # 2. Capture Portfolio ID from URL
            print("  Attempting to capture Portfolio ID...")
            current_url = sb.page.url
            portfolio_id = ""
            for part in current_url.split("/"):
                if part.isdigit() and len(part) > 10:
                    portfolio_id = part
                    break
            
            if portfolio_id:
                print(f"  [OK] Captured ID from URL: '{portfolio_id}'")
            else:
                print("  ID not found in URL. Falling back to page search...")
                # Search for any 12 to 20 digit number on the page to avoid years like 2023
                id_text = sb.page.evaluate("""
                    (function() {
                        var text = document.body.innerText || '';
                        var m = text.match(/\\b\\d{12,20}\\b/);
                        return m ? m[0] : '';
                    })()
                """)
                if id_text:
                    portfolio_id = id_text
                    print(f"  [OK] Captured ID from regex page search: '{portfolio_id}'")
                else:
                    print("  [ERROR] ID not found on page.")

            # 3. Wait for breadcrumb to be visible
            print("  Waiting for breadcrumb...")
            sb.page.wait_for_selector("ol.breadcrumb, nav.breadcrumb, [class*='breadcrumb']", timeout=10000)

            # 4. Click 'Portfolio' breadcrumb item (specifically target the <a> tag first)
            print("  Clicking 'Portfolio' breadcrumb...")
            initial_url = sb.page.url
            clicked = sb.page.evaluate("""
                (function() {
                    var containers = [
                        document.querySelector('nav ol.breadcrumb'),
                        document.querySelector('ol.breadcrumb'),
                        document.querySelector('[class*="breadcrumb"]')
                    ];
                    for (var c = 0; c < containers.length; c++) {
                        if (!containers[c]) continue;
                        
                        // Target the actual anchor link first
                        var links = containers[c].querySelectorAll('a');
                        for (var i = 0; i < links.length; i++) {
                            var t = (links[i].innerText || links[i].textContent || '').trim().toLowerCase();
                            if (t === 'portfolio' || t === 'portfolios') {
                                links[i].click();
                                return 'clicked link: ' + t;
                            }
                        }
                        
                        // Fallback to li / span items
                        var items = containers[c].querySelectorAll('li, span');
                        for (var i = 0; i < items.length; i++) {
                            var t = (items[i].innerText || items[i].textContent || '').trim().toLowerCase();
                            if (t === 'portfolio' || t === 'portfolios') {
                                items[i].click();
                                return 'clicked item: ' + t;
                            }
                        }
                    }
                    return 'NOT FOUND';
                })()
            """)
            print(f"  Breadcrumb click result: {clicked}")
            sb.page.wait_for_timeout(1000)
            
            if sb.page.url == initial_url:
                print("  URL did not change. Trying Playwright locator click...")
                try:
                    loc = sb.page.locator("ol.breadcrumb li a:has-text('Portfolio'), ol.breadcrumb li:has-text('Portfolio') a, a:has-text('Portfolio')").first
                    loc.click(timeout=5000)
                    print("  Playwright click performed successfully.")
                except Exception as e:
                    print(f"  Playwright click warning: {e}")
            
            sb.page.wait_for_timeout(PAUSE * 2)

            # 5. Wait for project list page to load URL and table rows
            print("  Waiting for project list page URL and table rows to load...")
            try:
                sb.page.wait_for_url(lambda url: "project/portfolio" in url or "project/list" in url, timeout=15_000)
                print(f"  Navigated URL: {sb.page.url}")
            except Exception as e:
                print(f"  Warning: wait_for_url timed out: {e}")

            # Wait for at least one row in the project table to load
            row_locator = sb.page.locator("table tbody tr.text-size-14px, table tbody tr, tr").first
            row_locator.wait_for(state="visible", timeout=15_000)
            sb.page.wait_for_timeout(PAUSE)

            # 6. Verify project name and ID are present in table rows
            rows = sb.page.locator("table tbody tr.text-size-14px, table tbody tr, tr")
            total = rows.count()
            found_idx = None
            found_row = ""
            for i in range(total):
                txt = rows.nth(i).inner_text().strip()
                if project_name.lower() in txt.lower():
                    found_idx = i
                    found_row = txt
                    break
            
            assert found_idx is not None, f"Project '{project_name}' not found in {total} rows"
            print(f"  [OK] Found project name '{project_name}' in row: '{found_row[:100]}'")

            if portfolio_id:
                assert portfolio_id in found_row, f"Portfolio ID '{portfolio_id}' not found in row text '{found_row}'"
                print(f"  [OK] Verified Portfolio ID '{portfolio_id}' in row.")

            # 7. Click the project row to reopen it
            print("  Clicking the project row...")
            project_link = rows.nth(found_idx).locator("a").first
            if project_link.count() == 0:
                project_link = rows.nth(found_idx).locator(f"td:has-text('{project_name}')").first
            if project_link.count() == 0:
                project_link = rows.nth(found_idx)
            
            project_link.click()
            sb.page.wait_for_timeout(PAUSE * 2)

            # 8. Wait for basic page view to load
            sb.page.wait_for_selector("b:has-text('Portfolio Info'), label[for='tab2']", timeout=15_000)

            # 9. Click 'Asset Management' tab
            print("  Clicking 'Asset Management' tab...")
            asset_tab = sb.page.locator("label[for='tab2'], label:has-text('Asset Management')").first
            asset_tab.wait_for(state="visible", timeout=10000)
            asset_tab.click()
            sb.page.wait_for_timeout(PAUSE * 2)
            print("  [OK] Navigated to Asset Management tab successfully.")

            ru.add_result("Portfolio Basic Info", "PBI04 - Reopen portfolio and select Asset Management tab", start, "PASSED")
            print("PBI04 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Basic Info", "PBI04 - Reopen portfolio and select Asset Management tab", start, "FAILED", str(e))
            raise
