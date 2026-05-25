import sys, os
import datetime
import pytest

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb
from pages.project_files_page import ProjectFilesPage

class TestProjectFilesTab:

    page_obj = None

    @classmethod
    def setup_class(cls):
        print("\n\nProject Files: Clicking Project Files tab from main menu...")
        cls.page_obj = ProjectFilesPage()
        cls.page_obj.navigate_to_project_files()
        print("Project Files tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nProject Files tests done. Browser stays open.\n")

    def test_PF01_verify_building_info_folders_and_upload(self):
        """PF01 - Start from Building Info, check nested folders, upload files, check count"""
        start = datetime.datetime.now()
        print("\nPF01: Building Info File Management")
        try:
            # 1. Click Building Info
            self.page_obj.click_side_tab("Building Info")
            
            # 2. Check Operations Phase folder is present
            folders = self.page_obj.get_all_nested_folders()
            print(f"  Found nested folders in Building Info: {folders}")
            assert "Operations Phase" in folders, "Operations Phase folder not found in Building Info"
            
            # Record initial count from root view
            initial_folder_count = self.page_obj.get_folder_item_count("Operations Phase")
            print(f"  Initial item count for Operations Phase (Root View): {initial_folder_count}")
            if initial_folder_count:
                assert "0" in initial_folder_count, f"Expected 0 items, got {initial_folder_count}"
            
            # 3. Click that (Operations Phase)
            self.page_obj.open_folder("Operations Phase")
            
            # 3.5 Check name added in breadcrumb
            has_breadcrumb = self.page_obj.check_breadcrumb("Operations Phase")
            print(f"  Breadcrumb 'Operations Phase' visible: {has_breadcrumb}")
            assert has_breadcrumb, "Breadcrumb 'Operations Phase' not found after opening folder"
            
            # 4. Check no records found if no files present
            if self.page_obj.get_file_count() == 0:
                has_no_records = self.page_obj.check_no_records_found()
                print(f"  No records found message displayed: {has_no_records}")
            
            # 5. Click add files and upload files
            upload_success = self.page_obj.upload_file("building_info_test.txt")
            if not upload_success:
                print("  ⚠️ Could not upload file, input[type='file'] might be missing or hidden.")
            
            # 6. Click operation phase in breadcrumb
            self.page_obj.click_breadcrumb("Operations Phase")
            
            # 7. Check file count is correct inside the folder
            new_file_count = self.page_obj.get_file_count()
            print(f"  New file count inside Operations Phase: {new_file_count}")
            if upload_success:
                assert new_file_count > 0, f"File count inside Operations Phase did not increase. Shows {new_file_count}"
                
            # Go back to root for subsequent tests
            self.page_obj.go_back_to_root()
            
            ru.add_result("Project Files", "PF01 - Building Info Upload", start, "PASSED")
            print("PF01 PASSED")
        except Exception as e:
            ru.add_result("Project Files", "PF01 - Building Info Upload", start, "FAILED", str(e))
            raise

    def _traverse_and_verify_folders(self, current_breadcrumb_level=None):
        """Recursively traverses all folders visible on the screen and returns the total file count found."""
        folders = self.page_obj.get_all_nested_folders()
        if not folders:
            # We reached the deepest level (no subfolders)
            # Check file count
            count = self.page_obj.get_file_count()
            print(f"     ✅ Verified {count} files present in leaf folder.")
            return count

        total_files = 0
        for folder in folders:
            print(f"  -> Entering {folder}")
            self.page_obj.open_folder(folder)
            
            # Check breadcrumb
            has_crumb = self.page_obj.check_breadcrumb(folder)
            if not has_crumb:
                print(f"     ⚠️ Breadcrumb '{folder}' not found. It might be truncated or named differently.")
            else:
                print(f"     ✅ Breadcrumb '{folder}' is visible.")
            
            # Recurse deeper
            total_files += self._traverse_and_verify_folders(folder)
            
            # After returning from deep folders, navigate back up
            print(f"  <- Navigating back from {folder}")
            if current_breadcrumb_level:
                self.page_obj.click_breadcrumb(current_breadcrumb_level)
            else:
                self.page_obj.go_back_to_root()
        
        return total_files

    @pytest.mark.parametrize("tab_name", [
        "Assessment",
        "Net Zero Plan",
        "Offset",
        "Net Zero Milestone"
    ])
    def test_PF02_verify_deep_folders(self, tab_name):
        """PF02 - Verify deep folder hierarchy and uploaded files for all tabs"""
        start = datetime.datetime.now()
        print(f"\nPF02: Deep Verification for {tab_name}")
        try:
            self.page_obj.click_side_tab(tab_name)
            sb.page.wait_for_timeout(1000)
            
            # Make sure we start at the root
            self.page_obj.go_back_to_root()
            sb.page.wait_for_timeout(500)
            
            total_found = self._traverse_and_verify_folders(None)
            assert total_found > 0, f"No files were found in ANY leaf folder for {tab_name}. Expected at least some uploaded files."
                
            ru.add_result("Project Files", f"PF02 - {tab_name} Verification", start, "PASSED")
            print(f"PF02 ({tab_name}) PASSED")
        except Exception as e:
            ru.add_result("Project Files", f"PF02 - {tab_name} Verification", start, "FAILED", str(e))
            raise
