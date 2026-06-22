import sys, os
import datetime
import pytest

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb
from pages.overview_page import OverviewPage

class TestOverviewTab:
    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nOverview: Clicking Overview tab from main menu...")
        cls.page_obj = OverviewPage()
        cls.page_obj.navigate_to_overview()
        print("Overview tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nOverview tests done. Browser stays open.\n")

    def test_OV01_verify_overview_fields_and_submit_assessment(self):
        """OV01 - Check all fields in overview, submit assessment for review, verify error"""
        start = datetime.datetime.now()
        print("\nOV01: Verify Overview fields and error message")
        try:
            # 1. Check all fields
            print("  Checking all fields in Overview...")
            assert self.page_obj.are_all_fields_visible(), "Not all Overview dropdown fields are visible."
            print("  ✅ All fields are present.")
            
            # 2. Select 'Submit for review' in complete assessment
            print("  Selecting 'Submit for review' in Complete assessment...")
            self.page_obj.submit_assessment_for_review()
            
            # 3. Check error message
            error_msg = self.page_obj.get_error_message()
            expected_msgs = [
                "Please submit the assessment for certification after completing the Basic Info tab.",
                "Please submit the assessment for certification after completing the Asset Info tab.",
                "Please submit the assessment for certification after completing the Building Info tab."
            ]
            
            assert any(msg in error_msg for msg in expected_msgs), f"Error message mismatch. Got: '{error_msg}'"
            print(f"  ✅ Caught expected error message: '{error_msg}'")
            
            # 4. Change status of all dropdowns to 'Completed'
            first_label = "Building Info"
            if sb.page.locator(".text-label:has-text('Asset Info'), label:has-text('Asset Info'), .form-label:has-text('Asset Info'), text='Asset Info'").first.is_visible():
                first_label = "Asset Info"
            elif sb.page.locator(".text-label:has-text('Basic Info'), label:has-text('Basic Info'), .form-label:has-text('Basic Info'), text='Basic Info'").first.is_visible():
                first_label = "Basic Info"

            dropdowns = [
                (first_label, self.page_obj.building_info_select),
                ("Team Info", self.page_obj.team_info_select),
                ("Net Zero Plans", self.page_obj.net_zero_plans_select),
                ("Complete Assessment", self.page_obj.complete_assessment_select)
            ]
            
            for name, locator in dropdowns:
                print(f"  Changing status of '{name}' to Completed...")
                self.page_obj.change_status_and_confirm(locator, "Completed")
                status = self.page_obj.get_selected_status(locator)
                print(f"  '{name}' status is now: '{status}'")
                assert status == "Completed", f"Expected '{name}' status to be Completed, got '{status}'"
            
            ru.add_result("Overview", "OV01 - Overview Fields and Submit", start, "PASSED")
            print("OV01 PASSED")
        except Exception as e:
            ru.add_result("Overview", "OV01 - Overview Fields and Submit", start, "FAILED", str(e))
            raise

    def test_OV02_return_to_list_and_verify_details(self):
        """OV02 - Go back to List of Assets, expand building row, verify all detailed values, and check top summary stats"""
        start = datetime.datetime.now()
        print("\nOV02: Return to List of Assets and verify details/summary view")
        try:
            # 1. Click portfolio name in breadcrumb to return to list of assets
            print("  Clicking portfolio name breadcrumb to return to list of assets...")
            breadcrumb_selectors = [
                "ol.breadcrumb a:has-text('Portfolio -')",
                "nav.breadcrumb a:has-text('Portfolio -')",
                "a:has-text('Portfolio -')",
                "ol.breadcrumb li a",
                ".breadcrumbs a"
            ]
            
            portfolio_breadcrumb = None
            for sel in breadcrumb_selectors:
                locs = sb.page.locator(sel)
                count = locs.count()
                for i in range(count):
                    txt = locs.nth(i).inner_text().strip()
                    print(f"    Checking breadcrumb candidate: '{txt}'")
                    if "portfolio" in txt.lower() and "building" not in txt.lower() and txt.lower() not in ["portfolio", "portfolios"]:
                        portfolio_breadcrumb = locs.nth(i)
                        print(f"      [FOUND] Target portfolio breadcrumb: '{txt}'")
                        break
                if portfolio_breadcrumb:
                    break
            
            if not portfolio_breadcrumb:
                for parent_sel in ["ol.breadcrumb", ".breadcrumbs", "nav.breadcrumb"]:
                    parent_loc = sb.page.locator(parent_sel).first
                    if parent_loc.count() > 0:
                        anchors = parent_loc.locator("a")
                        if anchors.count() >= 3:
                            portfolio_breadcrumb = anchors.nth(2)
                            print(f"      [FALLBACK] Using 3rd breadcrumb anchor: '{portfolio_breadcrumb.inner_text().strip()}'")
                            break
                            
            assert portfolio_breadcrumb is not None, "Could not find portfolio name breadcrumb to click!"
            portfolio_breadcrumb.click()
            sb.page.wait_for_timeout(3000)

            # 2. Wait for List of Assets page to load
            print("  Waiting for List of Assets page...")
            LIST_OF_ASSETS_HEADER = "b:has-text('List of Assets')"
            sb.page.wait_for_selector(LIST_OF_ASSETS_HEADER, timeout=15000)
            sb.page.wait_for_timeout(1000)

            # 3. Locate the row for the building/asset
            print("  Locating building row in assets table...")
            found_row = None
            rows = sb.page.locator("table tbody tr")
            for i in range(rows.count()):
                txt = rows.nth(i).inner_text().strip().lower()
                if "building" in txt:
                    found_row = rows.nth(i)
                    print(f"    Found building row: '{rows.nth(i).inner_text().strip()}'")
                    break
            
            assert found_row is not None, "Could not find any building row in List of Assets!"

            # 4. Click chevron-down expansion icon/td inside the row
            print("  Clicking expansion chevron inside the row...")
            chevron_td = found_row.locator("td.action-min-width.pointer, td.action-min-width, span.cursor-pointer:has(i.bi-chevron-down), i.bi-chevron-down").first
            try:
                chevron_td.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            chevron_td.click()
            sb.page.wait_for_timeout(2000)

            # 5. Wait for expanded details container to be visible
            print("  Waiting for expanded details container...")
            details_container = sb.page.locator(".cardd, gnfz-summary-details").first
            details_container.wait_for(state="visible", timeout=10000)

            # 6. Helper to get value next to label in the expanded details area
            def get_detail_value(label_text):
                loc = details_container.locator(f"div.details-row:has(p:has-text('{label_text}')) p").last
                try:
                    loc.scroll_into_view_if_needed(timeout=5000)
                except Exception as e:
                    print(f"    Detail value scroll timeout for '{label_text}', using JS scroll: {e}")
                    sb.page.evaluate("arguments[0].scrollIntoView(true);", loc.element_handle())
                    sb.page.wait_for_timeout(500)
                return loc.inner_text().strip()

            # Verify all detailed values:
            # - Asset ID
            asset_id_val = get_detail_value("Asset ID")
            print(f"    Asset ID: '{asset_id_val}'")
            assert asset_id_val.isdigit(), f"Expected Asset ID to be numeric, got: '{asset_id_val}'"

            # - Approach
            approach_val = get_detail_value("Approach")
            print(f"    Approach: '{approach_val}'")
            assert "operations" in approach_val.lower(), f"Expected Approach containing 'operations', got '{approach_val}'"

            # - Location
            location_val = get_detail_value("Location")
            print(f"    Location: '{location_val}'")
            assert "marina" in location_val.lower() or "beach" in location_val.lower(), f"Expected Location containing 'Marina Beach', got '{location_val}'"

            # - Gross area
            gross_val = get_detail_value("Gross area")
            print(f"    Gross area: '{gross_val}'")
            assert "100" in gross_val, f"Expected Gross area containing '100', got '{gross_val}'"

            # - Target certification area
            target_val = get_detail_value("Target certification area")
            print(f"    Target certification area: '{target_val}'")
            assert "100" in target_val, f"Expected Target certification area containing '100', got '{target_val}'"
            print("  [PASS] All asset detailed values verified successfully.")

            # 7. Check summary stats values (Total assets, Total gross area, Total target certification area)
            print("  Verifying top summary stats block...")
            summary_container = sb.page.locator("div.text-size-14px:has-text('Total assets'), .text-size-14px:has-text('Total assets')").first
            summary_container.wait_for(state="visible", timeout=10000)
            summary_text = summary_container.inner_text().strip()
            print(f"  Summary block text:\n{summary_text}")
            
            normalized_summary = " ".join(summary_text.split())
            assert "Total assets" in normalized_summary and "1" in normalized_summary, \
                f"Expected Total assets containing '1' but got: '{normalized_summary}'"
            assert "Total gross area" in normalized_summary and "100" in normalized_summary, \
                f"Expected Total gross area containing '100' but got: '{normalized_summary}'"
            assert "Total target certification area" in normalized_summary and "100" in normalized_summary, \
                f"Expected Total target certification area containing '100' but got: '{normalized_summary}'"
            print("  [PASS] Top summary stats values verified successfully.")

            ru.add_result("Overview", "OV02 - Return to List and Verify Details/Summary", start, "PASSED")
            print("OV02 PASSED")
        except Exception as e:
            ru.add_result("Overview", "OV02 - Return to List and Verify Details/Summary", start, "FAILED", str(e))
            raise

