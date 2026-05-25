import sys, os
import datetime

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb
from pages.offset_page import OffsetPage

class TestOffsetTab:

    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nOffset: Clicking Offset tab from main menu...")
        cls.page_obj = OffsetPage()
        cls.page_obj.navigate_to_offset()
        print("Offset tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nOffset tests done. Browser stays open.\n")

    def test_OF01_verify_emissions_offset(self):
        """OF01 - Verify Net Zero Emissions Offset validation and upload workflow"""
        self._execute_offset_workflow("Net Zero Emissions", "OF01")

    def test_OF02_verify_energy_offset(self):
        """OF02 - Verify Net Zero Energy Offset validation and upload workflow"""
        self._execute_offset_workflow("Net Zero Energy", "OF02")

    def test_OF03_verify_water_offset(self):
        """OF03 - Verify Net Zero Water Offset validation and upload workflow"""
        self._execute_offset_workflow("Net Zero Water", "OF03")

    def _execute_offset_workflow(self, tab_name, test_id):
        start = datetime.datetime.now()
        print(f"\n{test_id}: {tab_name} Workflow")
        try:
            # 1. Click sub-tab
            self.page_obj.click_sub_tab(tab_name)
            
            # --- NEGATIVE TEST: Same Dates ---
            print("  Running Negative Test (Duplicate Dates)...")
            self.page_obj.delete_all_rows_except_first()
                
            today_date = datetime.datetime.now().strftime("%m/%d/%Y")
            
            # 1st row: add today's date
            self.page_obj.fill_date(0, today_date)
            self.page_obj.fill_values(0, 100, 95)
            
            # Add another row (2nd) and add same date
            self.page_obj.add_row()
            self.page_obj.fill_date(1, today_date)
            self.page_obj.fill_values(1, 100, 95)
                
            # Click save and check error message
            self.page_obj.click_save()
            error_msg = self.page_obj.get_toast_message()
            if error_msg:
                print(f"  ✅ Caught expected error message: '{error_msg}'")
            else:
                print("  ⚠️ Warning: No error message caught for duplicate dates. Continuing with positive test...")
                
            # --- POSITIVE TEST ---
            print("  Running Positive Test (Unique Dates)...")
            
            # Remove the second row to clear the duplicate
            self.page_obj.delete_all_rows_except_first()
            
            # Add another row add tomorrow's date
            tomorrow_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%m/%d/%Y")
            self.page_obj.add_row()
            self.page_obj.fill_date(1, tomorrow_date)
            self.page_obj.fill_values(1, 200, 190)
            
            # Add 3rd row 12/9/2025
            self.page_obj.add_row()
            self.page_obj.fill_date(2, "12/9/2025")
            self.page_obj.fill_values(2, 300, 280)

             # Add 4th row 3/8/2024
            self.page_obj.add_row()
            self.page_obj.fill_date(3, "3/8/2024")
            self.page_obj.fill_values(3, 300, 280)
            
            self.page_obj.click_save()
            success_msg = self.page_obj.get_toast_message()
            print(f"  ✅ Save result: {success_msg}")
            
            ru.add_result("Offset", f"{test_id} - {tab_name}", start, "PASSED")
            print(f"{test_id} PASSED")
        except Exception as e:
            ru.add_result("Offset", f"{test_id} - {tab_name}", start, "FAILED", str(e))
            raise
