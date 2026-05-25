import sys, os
import datetime

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
from pages.net_zero_plan_page import NetZeroPlanPage

class TestNetZeroPlanTab:

    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nNet Zero Plan: Clicking Net Zero Plan tab from main menu...")
        cls.page_obj = NetZeroPlanPage()
        cls.page_obj.navigate_to_net_zero_plan()
        print("Net Zero Plan tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nNet Zero Plan tests done. Browser stays open.\n")

    def test_NZP01_verify_emissions_workflow(self):
        """NZP01 - Verify Net Zero Plan sub-tabs and Emissions upload workflow"""
        start = datetime.datetime.now()
        print("\nNZP01: Net Zero Emissions Workflow")
        try:
            # 1. Verify Four Tabs
            print("  Verifying four sub-tabs...")
            tabs = ["Net Zero Emissions", "Net Zero Energy", "Net Zero Water", "Net Zero Waste"]
            for tab in tabs:
                assert self.page_obj.is_sub_tab_present(tab), f"Missing sub-tab: {tab}"
            print("  ✅ All four sub-tabs present.")

            # 2. Click Net Zero Emissions
            self.page_obj.click_sub_tab("Net Zero Emissions")

            # 3. Check tooltip
            tooltip_text = self.page_obj.get_tooltip_text()
            assert "The net zero plan is a narrative document" in tooltip_text, f"Unexpected tooltip: {tooltip_text}"
            print("  ✅ Tooltip text verified.")

            # 4. Click View/Upload
            self.page_obj.click_view_upload()
            
            # 5. Verify "Net Zero Plan" active status title
            status_title = self.page_obj.get_active_status_title()
            assert "Net Zero Plan" in status_title, f"Active status title mismatch. Got: {status_title}"
            print("  ✅ Status title 'Net Zero Plan' verified.")
            
            # 6. Verify Breadcrumbs
            bc_text = self.page_obj.get_breadcrumbs_text()
            assert "Net Zero Emissions" in bc_text, f"Breadcrumb missing 'Net Zero Emissions'. Got: {bc_text}"
            print(f"  ✅ Breadcrumbs verified: {bc_text.replace(chr(10), ' > ')}")

            # 7. Upload File
            print("  Uploading file...")
            uploaded = self.page_obj.upload_dummy_file()
            assert uploaded, "File upload failed or buttons missing."
            
            # 8. Close panel
            self.page_obj.close_file_panel()
            print("  ✅ Panel closed.")

            ru.add_result("Net Zero Plan", "NZP01 - Emissions Workflow", start, "PASSED")
            print("NZP01 PASSED")
        except Exception as e:
            ru.add_result("Net Zero Plan", "NZP01 - Emissions Workflow", start, "FAILED", str(e))
            raise

    def test_NZP02_verify_energy_workflow(self):
        """NZP02 - Verify Net Zero Energy upload workflow"""
        start = datetime.datetime.now()
        print("\nNZP02: Net Zero Energy Workflow")
        try:
            self.page_obj.click_sub_tab("Net Zero Energy")
            self.page_obj.click_view_upload()

            # Verify Breadcrumbs
            bc_text = self.page_obj.get_breadcrumbs_text()
            assert "Net Zero Energy" in bc_text, f"Breadcrumb missing 'Net Zero Energy'. Got: {bc_text}"
            print(f"  ✅ Breadcrumbs verified: {bc_text.replace(chr(10), ' > ')}")

            # Upload File
            print("  Uploading file...")
            uploaded = self.page_obj.upload_dummy_file()
            assert uploaded, "File upload failed or buttons missing."
            
            # Close panel
            self.page_obj.close_file_panel()
            print("  ✅ Panel closed.")

            ru.add_result("Net Zero Plan", "NZP02 - Energy Workflow", start, "PASSED")
            print("NZP02 PASSED")
        except Exception as e:
            ru.add_result("Net Zero Plan", "NZP02 - Energy Workflow", start, "FAILED", str(e))
            raise

    def test_NZP03_verify_water_workflow(self):
        """NZP03 - Verify Net Zero Water upload workflow"""
        start = datetime.datetime.now()
        print("\nNZP03: Net Zero Water Workflow")
        try:
            self.page_obj.click_sub_tab("Net Zero Water")
            self.page_obj.click_view_upload()

            # Verify Breadcrumbs
            bc_text = self.page_obj.get_breadcrumbs_text()
            assert "Net Zero Water" in bc_text, f"Breadcrumb missing 'Net Zero Water'. Got: {bc_text}"
            print(f"  ✅ Breadcrumbs verified: {bc_text.replace(chr(10), ' > ')}")

            # Upload File
            print("  Uploading file...")
            uploaded = self.page_obj.upload_dummy_file()
            assert uploaded, "File upload failed or buttons missing."
            
            # Close panel
            self.page_obj.close_file_panel()
            print("  ✅ Panel closed.")

            ru.add_result("Net Zero Plan", "NZP03 - Water Workflow", start, "PASSED")
            print("NZP03 PASSED")
        except Exception as e:
            ru.add_result("Net Zero Plan", "NZP03 - Water Workflow", start, "FAILED", str(e))
            raise

    def test_NZP04_verify_waste_workflow(self):
        """NZP04 - Verify Net Zero Waste upload workflow"""
        start = datetime.datetime.now()
        print("\nNZP04: Net Zero Waste Workflow")
        try:
            self.page_obj.click_sub_tab("Net Zero Waste")
            self.page_obj.click_view_upload()

            # Verify Breadcrumbs
            bc_text = self.page_obj.get_breadcrumbs_text()
            assert "Net Zero Waste" in bc_text, f"Breadcrumb missing 'Net Zero Waste'. Got: {bc_text}"
            print(f"  ✅ Breadcrumbs verified: {bc_text.replace(chr(10), ' > ')}")

            # Upload File
            print("  Uploading file...")
            uploaded = self.page_obj.upload_dummy_file()
            assert uploaded, "File upload failed or buttons missing."
            
            # Close panel
            self.page_obj.close_file_panel()
            print("  ✅ Panel closed.")

            ru.add_result("Net Zero Plan", "NZP04 - Waste Workflow", start, "PASSED")
            print("NZP04 PASSED")
        except Exception as e:
            ru.add_result("Net Zero Plan", "NZP04 - Waste Workflow", start, "FAILED", str(e))
            raise
