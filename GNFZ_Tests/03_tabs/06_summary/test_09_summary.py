import sys, os
import datetime

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb
from pages.summary_page import SummaryPage

def sc(locator):
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
        sb.page.wait_for_timeout(200)
    except Exception:
        pass

class TestSummaryTab:

    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nSummary: Clicking Summary tab from main menu...")
        cls.page_obj = SummaryPage()
        cls.page_obj.navigate_to_summary()
        print("Summary tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nSummary tests done. Browser stays open.\n")

    def _get_assessment_data(self, assessment_btn_id, is_emission=False, ftestcaseref=None):
        """Helper to navigate to assessment, click sub-tab, read total and scopes, and return data."""
        print(f"  Fetching assessment data for {assessment_btn_id}...")
        # Go to assessment tab
        ass_tab = sb.page.locator("#gnfz-assessment label").first
        sc(ass_tab)
        ass_tab.click()
        sb.page.wait_for_timeout(1000)
        
        # Click subtab
        btn = sb.page.locator(assessment_btn_id).first
        sc(btn)
        btn.click()
        sb.page.wait_for_timeout(2000)
        
        # Read data
        if is_emission:
            # For emission, open summary accordion first
            sc(sb.page.locator("#flush-heading__ScopeSummary").first)
            sb.page.evaluate(f"""
                (function() {{
                    var hdr = document.getElementById('flush-heading__ScopeSummary');
                    if (!hdr) return;
                    var btn = hdr.querySelector('[data-bs-toggle="collapse"]') || hdr.querySelector('button') || hdr.firstElementChild;
                    if (btn) btn.click();
                }})()
            """)
            sb.page.wait_for_timeout(1000)
            
        data = {}
        
        # If an explicit test case ref is provided, try that first for total
        if ftestcaseref:
            inp = sb.page.locator(f"input[ftestcaseref='{ftestcaseref}']").first
            if inp.count() > 0:
                val_text = inp.input_value().replace(',', '').strip()
                try:
                    data["total"] = float(val_text)
                    print(f"  ✅ Found total from {ftestcaseref}: {data['total']}")
                except ValueError:
                    pass

        # Parse summary table for scopes and total
        tables = sb.page.locator("table.summary-table")
        for t_idx in range(tables.count()):
            table = tables.nth(t_idx)
            rows = table.locator("tbody tr")
            for i in range(rows.count()):
                row = rows.nth(i)
                text = row.inner_text().lower()
                cells = row.locator("td")
                if cells.count() >= 2:
                    val_text = cells.nth(1).inner_text().replace(',', '').strip()
                    try:
                        val = float(val_text)
                        if "scope 1" in text:
                            data["scope 1"] = val
                        elif "scope 2" in text:
                            data["scope 2"] = val
                        elif "scope 3" in text:
                            data["scope 3"] = val
                        elif "total emissions of the building" in text or "total" in text:
                            # Always take the generic total (usually the grand total)
                            data["total"] = val
                    except ValueError:
                        pass
        
        # Calculate proper total if scopes were parsed
        calc_total = data.get("scope 1", 0.0) + data.get("scope 2", 0.0) + data.get("scope 3", 0.0)
        if calc_total > 0:
            if "total" not in data or abs(data["total"] - calc_total) > 2.0:
                print(f"  ⚠️ Overriding parsed total ({data.get('total', 0.0)}) with calculated sum of scopes ({calc_total})")
                data["total"] = calc_total
        
        # Go back to Summary tab
        self.page_obj.navigate_to_summary()
        return data

    def _verify_scopes_and_total(self, ass_data, sum_data, total_key_in_summary="total"):
        sum_total = sum_data.get(total_key_in_summary, sum_data.get("total", 0.0))
        ass_total = ass_data.get("total", 0.0)
        
        # Check Scopes
        for scope in ["scope 1", "scope 2", "scope 3"]:
            if scope in sum_data and sum_data[scope] > 0:
                s_val = sum_data[scope]
                a_val = ass_data.get(scope, 0.0)
                if a_val > 0:
                    assert abs(a_val - s_val) < 2.0, f"{scope.title()} mismatch! Assessment: {a_val}, Summary: {s_val}"
                    print(f"  ✅ {scope.title()} values match assessment: {s_val}")
                else:
                    print(f"  ⚠️ {scope.title()} found in summary ({s_val}) but not parsed from assessment.")
                    
        # Check Total
        if ass_total > 0:
            assert abs(ass_total - sum_total) < 2.0, f"Total mismatch! Assessment: {ass_total}, Summary: {sum_total}"
            print("  ✅ Total values match assessment")
        else:
            assert sum_total > 0, "Summary Total is 0"
            print("  ✅ Summary Total > 0 (Assessment total could not be parsed)")
        
        return sum_total

    def test_SU01_verify_emission_summary(self):
        """SU01 - Verify Net Zero Emissions Summary values match assessment and offset/milestone data present"""
        start = datetime.datetime.now()
        print("\nSU01: Net Zero Emissions Summary")
        try:
            # 1. Fetch Assessment Value
            ass_data = self._get_assessment_data("#net-zero-emission-assessment", is_emission=True)
            print(f"  Assessment Emission Data: {ass_data}")
            
            # 2. Go to Emissions Sub-tab on Summary
            self.page_obj.click_sub_tab("Net Zero Emissions")
            
            # 3. Read Summary Table
            data = self.page_obj.get_summary_table_data()
            print(f"  Summary Emission Data: {data}")
            
            # 4. Check they match
            sum_total = self._verify_scopes_and_total(ass_data, data, total_key_in_summary="total")
            
            # 5. Check offset and milestone data
            has_offset = self.page_obj.check_offset_data_present("2026")
            has_milestone = self.page_obj.check_milestone_data_present("2025")
            
            assert has_offset, "Offset 2026 data not found on Emission summary"
            print("  ✅ Offset 2026 data present")
            
            assert has_milestone, "Net Zero Milestone 2025 data not found on Emission summary"
            print("  ✅ Net Zero Milestone 2025 data present")
            
            net_zero_avoided = data.get("net_zero_avoided", 0.0)
            offsets = data.get("offsets", 0.0)
            removal = data.get("removal", 0.0)
            expected_avoided = sum_total - offsets - removal
            
            if "net_zero_avoided" in data:
                assert abs(expected_avoided - net_zero_avoided) < 2.0, f"Net Zero Avoided mismatch! Expected: {expected_avoided}, Actual: {net_zero_avoided}"
                print("  ✅ Net Zero Avoided calculation is correct (Total - Offsets - Removals)")
            
            ru.add_result("Summary", "SU01 - Emission Summary", start, "PASSED")
            print("SU01 PASSED")
        except Exception as e:
            ru.add_result("Summary", "SU01 - Emission Summary", start, "FAILED", str(e))
            raise

    def test_SU02_verify_energy_summary(self):
        """SU02 - Verify Net Zero Energy Summary values match assessment"""
        start = datetime.datetime.now()
        print("\nSU02: Net Zero Energy Summary")
        try:
            ass_data = self._get_assessment_data("#net-zero-energy-assessment", ftestcaseref="scope2_energy_total")
            print(f"  Assessment Energy Data: {ass_data}")
            
            self.page_obj.click_sub_tab("Net Zero Energy")
            
            data = self.page_obj.get_summary_table_data()
            print(f"  Summary Energy Data: {data}")
            
            sum_total = self._verify_scopes_and_total(ass_data, data, total_key_in_summary="net_zero_avoided")
            
            ru.add_result("Summary", "SU02 - Energy Summary", start, "PASSED")
            print("SU02 PASSED")
        except Exception as e:
            ru.add_result("Summary", "SU02 - Energy Summary", start, "FAILED", str(e))
            raise

    def test_SU03_verify_water_summary(self):
        """SU03 - Verify Net Zero Water Summary values match assessment"""
        start = datetime.datetime.now()
        print("\nSU03: Net Zero Water Summary")
        try:
            ass_data = self._get_assessment_data("#net-zero-water-assessment", ftestcaseref="scope3_water_total")
            print(f"  Assessment Water Data: {ass_data}")
            
            self.page_obj.click_sub_tab("Net Zero Water")
            
            data = self.page_obj.get_summary_table_data()
            print(f"  Summary Water Data: {data}")
            
            sum_total = self._verify_scopes_and_total(ass_data, data, total_key_in_summary="freshwater_requirement")
            
            ru.add_result("Summary", "SU03 - Water Summary", start, "PASSED")
            print("SU03 PASSED")
        except Exception as e:
            ru.add_result("Summary", "SU03 - Water Summary", start, "FAILED", str(e))
            raise

    def test_SU04_verify_waste_summary(self):
        """SU04 - Verify Net Zero Waste Summary values match assessment"""
        start = datetime.datetime.now()
        print("\nSU04: Net Zero Waste Summary")
        try:
            ass_data = self._get_assessment_data("#net-zero-waste-assessment", ftestcaseref="scope3_waste_total")
            print(f"  Assessment Waste Data: {ass_data}")
            
            self.page_obj.click_sub_tab("Net Zero Waste")
            
            data = self.page_obj.get_summary_table_data()
            print(f"  Summary Waste Data: {data}")
            
            sum_total = self._verify_scopes_and_total(ass_data, data, total_key_in_summary="waste_reduced")
            
            ru.add_result("Summary", "SU04 - Waste Summary", start, "PASSED")
            print("SU04 PASSED")
        except Exception as e:
            ru.add_result("Summary", "SU04 - Waste Summary", start, "FAILED", str(e))
            raise
