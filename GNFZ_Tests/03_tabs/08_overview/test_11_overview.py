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
            expected_msg = "Please submit the assessment for certification after completing the Basic Info tab."
            
            assert expected_msg in error_msg, f"Error message mismatch. Expected: '{expected_msg}', Got: '{error_msg}'"
            print(f"  ✅ Caught expected error message: '{error_msg}'")
            
            ru.add_result("Overview", "OV01 - Overview Fields and Submit", start, "PASSED")
            print("OV01 PASSED")
        except Exception as e:
            ru.add_result("Overview", "OV01 - Overview Fields and Submit", start, "FAILED", str(e))
            raise
