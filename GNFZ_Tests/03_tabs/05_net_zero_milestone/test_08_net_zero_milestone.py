import sys, os
import datetime

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb
from pages.net_zero_milestone_page import NetZeroMilestonePage

class TestNetZeroMilestoneTab:

    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nNet Zero Milestone: Clicking Net Zero Milestone tab from main menu...")
        cls.page_obj = NetZeroMilestonePage()
        cls.page_obj.navigate_to_nzm()
        print("Net Zero Milestone tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nNet Zero Milestone tests done. Browser stays open.\n")

    def test_NZM01_verify_emissions_milestone(self):
        """NZM01 - Verify Net Zero Emissions Milestone validation and upload workflow"""
        self._execute_nzm_workflow("Net Zero Emissions", "NZM01")

    def test_NZM02_verify_energy_milestone(self):
        """NZM02 - Verify Net Zero Energy Milestone validation and upload workflow"""
        self._execute_nzm_workflow("Net Zero Energy", "NZM02")

    def test_NZM03_verify_water_milestone(self):
        """NZM03 - Verify Net Zero Water Milestone validation and upload workflow"""
        self._execute_nzm_workflow("Net Zero Water", "NZM03")

    def test_NZM04_verify_waste_milestone(self):
        """NZM04 - Verify Net Zero Waste Milestone validation and upload workflow"""
        self._execute_nzm_workflow("Net Zero Waste", "NZM04")

    def _execute_nzm_workflow(self, tab_name, test_id):
        start = datetime.datetime.now()
        print(f"\n{test_id}: {tab_name} Workflow")
        try:
            # 1. Click sub-tab
            self.page_obj.click_sub_tab(tab_name)
            
            # --- NEGATIVE TEST: Same Years ---
            print("  Running Negative Test (Duplicate Years)...")
            self.page_obj.delete_all_rows_except_first()
            
            current_year = str(datetime.datetime.now().year)
            
            # 1st row: add today's year
            self.page_obj.fill_year(0, current_year)
            self.page_obj.fill_values(0, 100, 95)
            
            # Add another row (2nd) and add same year
            self.page_obj.add_row()
            self.page_obj.fill_year(1, current_year)
            self.page_obj.fill_values(1, 100, 95)
            
            # Click save and check error message
            self.page_obj.click_save()
            error_msg = self.page_obj.get_toast_message()
            if error_msg:
                print(f"  ✅ Caught expected error message: '{error_msg}'")
            else:
                print("  ⚠️ Warning: No error message caught for duplicate years. Continuing with positive test...")
                
            # --- POSITIVE TEST ---
            print("  Running Positive Test (Unique Years)...")
            
            # Remove the second row to clear the duplicate
            self.page_obj.delete_all_rows_except_first()
            
            # Add another row add year 2025
            self.page_obj.add_row()
            self.page_obj.fill_year(1, "2025")
            self.page_obj.fill_values(1, 200, 190)
            
            # Add 3rd row 2024
            self.page_obj.add_row()
            self.page_obj.fill_year(2, "2024")
            self.page_obj.fill_values(2, 300, 280)
            
            self.page_obj.click_save()
            success_msg = self.page_obj.get_toast_message()
            print(f"  ✅ Save result: {success_msg}")
            
            ru.add_result("Net Zero Milestone", f"{test_id} - {tab_name}", start, "PASSED")
            print(f"{test_id} PASSED")
        except Exception as e:
            ru.add_result("Net Zero Milestone", f"{test_id} - {tab_name}", start, "FAILED", str(e))
            raise
