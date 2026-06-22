import sys, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import datetime
import report_utils as ru
import shared_browser as sb
from playwright.sync_api import expect

# ── Locators ──────────────────────────────────────────────────────────────────
LIST_OF_ASSETS_HEADER = "b:has-text('List of Assets')"
SEARCH_INPUT          = "input#project-search[placeholder='Search']"
ADD_NEW_ASSET_BUTTON  = "button.btn-outline-gnfz:has-text('Add new asset')"
ASSET_NAME_HEADER     = "th:has-text('Asset name')"
CATEGORY_HEADER       = "th:has-text('Category')"
EMISSIONS_HEADER      = "th:has-text('Emissions based on')"
SCOPE_1_HEADER        = "th:has-text('Scope 1')"
SCOPE_2_HEADER        = "th:has-text('Scope 2')"
SCOPE_3_HEADER        = "th:has-text('Scope 3')"
NO_RECORDS_MESSAGE    = "span:has-text('No records to show')"

PAUSE = 1000

class TestPortfolioAssetManagementTab:

    @classmethod
    def setup_class(cls):
        print("\n\nPortfolio Asset Management: Waiting for List of Assets content...")
        sb.page.wait_for_selector(LIST_OF_ASSETS_HEADER, timeout=15_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Portfolio Asset Management ready.\n")

    def test_PAM01_verify_asset_management_elements(self):
        """PAM01 - Verify all UI components, table headers, and empty state message
        in the Asset Management tab"""
        start = datetime.datetime.now()
        print("\nPAM01: Verify Asset Management components")
        try:
            elements = [
                ("List of Assets Header", LIST_OF_ASSETS_HEADER),
                ("Search Input", SEARCH_INPUT),
                ("Add New Asset Button", ADD_NEW_ASSET_BUTTON),
                ("Asset Name Table Header", ASSET_NAME_HEADER),
                ("Category Table Header", CATEGORY_HEADER),
                ("Emissions Table Header", EMISSIONS_HEADER),
                ("Scope 1 Header", SCOPE_1_HEADER),
                ("Scope 2 Header", SCOPE_2_HEADER),
                ("Scope 3 Header", SCOPE_3_HEADER),
                ("No Records Message", NO_RECORDS_MESSAGE)
            ]

            missing = []
            for name, locator in elements:
                loc = sb.page.locator(locator).first
                # Wait up to 5s for elements to be visible
                try:
                    loc.wait_for(state="visible", timeout=5000)
                    print(f"  [OK] Checked: {name} is visible.")
                except Exception:
                    missing.append(name)
                    print(f"  [ERROR] Checked: {name} is NOT visible.")

            assert len(missing) == 0, f"Missing Asset Management elements: {missing}"
            
            ru.add_result("Portfolio Asset Management", "PAM01 - Asset Management elements verified", start, "PASSED")
            print("PAM01 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Asset Management", "PAM01 - Asset Management elements verified", start, "FAILED", str(e))
            raise

    def test_PAM02_click_add_new_asset(self):
        """PAM02 - Click Add new asset button and wait for Asset Info page to load"""
        start = datetime.datetime.now()
        print("\nPAM02: Click Add new asset button")
        try:
            add_btn = sb.page.locator(ADD_NEW_ASSET_BUTTON).first
            add_btn.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(300)
            add_btn.click()
            sb.page.wait_for_timeout(PAUSE * 2)

            # Wait for Asset Info header on the new page
            sb.page.wait_for_selector("b:has-text('Asset Info')", timeout=15_000)
            print("  [OK] Asset Info page loaded successfully.")
            
            ru.add_result("Portfolio Asset Management", "PAM02 - Click Add new asset button", start, "PASSED")
            print("PAM02 PASSED")
        except Exception as e:
            ru.add_result("Portfolio Asset Management", "PAM02 - Click Add new asset button", start, "FAILED", str(e))
            raise
