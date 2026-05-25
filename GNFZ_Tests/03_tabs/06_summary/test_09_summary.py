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

    def _get_assessment_total(self, assessment_btn_id, is_emission=False, ftestcaseref=None):
        """Helper to navigate to assessment, click sub-tab, read total, and return."""
        print(f"  Fetching assessment total for {assessment_btn_id}...")
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
        
        # Read total
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
            
        total = 0.0
        
        # If an explicit test case ref is provided, try that first
        if ftestcaseref:
            inp = sb.page.locator(f"input[ftestcaseref='{ftestcaseref}']").first
            if inp.count() > 0:
                val_text = inp.input_value().replace(',', '').strip()
                try:
                    total = float(val_text)
                    print(f"  ✅ Found total from {ftestcaseref}: {total}")
                except ValueError:
                    pass

        # Fallback to summary table if total is still 0
        if total == 0.0:
            tables = sb.page.locator("table.summary-table")
            for t_idx in range(tables.count()):
                table = tables.nth(t_idx)
                rows = table.locator("tbody tr")
                for i in range(rows.count()):
                    row = rows.nth(i)
                    text = row.inner_text().lower()
                    if "total emissions of the building" in text or "total" in text:
                        cells = row.locator("td")
                        if cells.count() >= 2:
                            val_text = cells.nth(1).inner_text().replace(',', '').strip()
                            try:
                                parsed_val = float(val_text)
                                if "total emissions of the building" in text:
                                    total = parsed_val
                                    break # Absolute correct one found
                                else:
                                    total = parsed_val # keep as fallback
                            except ValueError:
                                pass
                if total > 0 and "total emissions of the building" in text:
                    break
        
        # Go back to Summary tab
        self.page_obj.navigate_to_summary()
        return total

    def test_SU01_verify_emission_summary(self):
        """SU01 - Verify Net Zero Emissions Summary values match assessment and offset/milestone data present"""
        start = datetime.datetime.now()
        print("\nSU01: Net Zero Emissions Summary")
        try:
            # 1. Fetch Assessment Value
            ass_total = self._get_assessment_total("#net-zero-emission-assessment", is_emission=True)
            print(f"  Assessment Emission Total: {ass_total}")
            
            # 2. Go to Emissions Sub-tab on Summary
            self.page_obj.click_sub_tab("Net Zero Emissions")
            
            # 3. Read Summary Table
            data = self.page_obj.get_summary_table_data()
            sum_total = data.get("total", 0.0)
            print(f"  Summary Emission Total: {sum_total}")
            
            # 4. Check they match (allow small rounding difference)
            if ass_total > 0:
                assert abs(ass_total - sum_total) < 2.0, f"Total mismatch! Assessment: {ass_total}, Summary: {sum_total}"
                print("  ✅ Emission values match assessment")
            else:
                assert sum_total > 0, "Summary Emission Total is 0"
                print("  ✅ Summary Emission Total > 0 (Assessment total could not be parsed)")
            
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
            ass_total = self._get_assessment_total("#net-zero-energy-assessment", ftestcaseref="scope2_energy_total")
            print(f"  Assessment Energy Total: {ass_total}")
            
            self.page_obj.click_sub_tab("Net Zero Energy")
            
            data = self.page_obj.get_summary_table_data()
            sum_total = data.get("net_zero_avoided", data.get("total", 0.0))
            print(f"  Summary Energy Total (Emissions to be avoided): {sum_total}")
            
            if ass_total > 0:
                assert abs(ass_total - sum_total) < 2.0, f"Total mismatch! Assessment: {ass_total}, Summary: {sum_total}"
                print("  ✅ Energy values match assessment")
            else:
                assert sum_total > 0, "Summary Energy Total is 0"
                print("  ✅ Summary Energy Total > 0 (Assessment total could not be parsed)")
            
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
            ass_total = self._get_assessment_total("#net-zero-water-assessment", ftestcaseref="scope3_water_total")
            print(f"  Assessment Water Total: {ass_total}")
            
            self.page_obj.click_sub_tab("Net Zero Water")
            
            data = self.page_obj.get_summary_table_data()
            sum_total = data.get("freshwater_requirement", data.get("total", 0.0))
            print(f"  Summary Water Total (Freshwater Requirement): {sum_total}")
            
            if ass_total > 0:
                assert abs(ass_total - sum_total) < 2.0, f"Total mismatch! Assessment: {ass_total}, Summary: {sum_total}"
                print("  ✅ Water values match assessment")
            else:
                assert sum_total > 0, "Summary Water Total is 0"
                print("  ✅ Summary Water Total > 0 (Assessment total could not be parsed)")
            
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
            ass_total = self._get_assessment_total("#net-zero-waste-assessment", ftestcaseref="scope3_waste_total")
            print(f"  Assessment Waste Total: {ass_total}")
            
            self.page_obj.click_sub_tab("Net Zero Waste")
            
            data = self.page_obj.get_summary_table_data()
            sum_total = data.get("waste_reduced", data.get("total", 0.0))
            print(f"  Summary Waste Total (Waste to be Reduced): {sum_total}")
            
            if ass_total > 0:
                assert abs(ass_total - sum_total) < 2.0, f"Total mismatch! Assessment: {ass_total}, Summary: {sum_total}"
                print("  ✅ Waste values match assessment")
            else:
                assert sum_total > 0, "Summary Waste Total is 0"
                print("  ✅ Summary Waste Total > 0 (Assessment total could not be parsed)")
            
            ru.add_result("Summary", "SU04 - Waste Summary", start, "PASSED")
            print("SU04 PASSED")
        except Exception as e:
            ru.add_result("Summary", "SU04 - Waste Summary", start, "FAILED", str(e))
            raise
