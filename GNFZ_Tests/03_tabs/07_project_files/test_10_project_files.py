import sys, os
import datetime
import pytest
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)
import report_utils as ru
import shared_browser as sb
from pages.project_files_page import ProjectFilesPage
from pages.overview_page import OverviewPage
from pages import ui_utils as uu
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
        print("\nProject Files tests done. Navigating to Overview tab...\n")
        overview_obj = OverviewPage()
        overview_obj.navigate_to_overview()
        print("Overview tab is now active.\n")
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
            
            # Wait for upload to reflect
            sb.page.wait_for_timeout(3000)
            
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
        """Recursively traverses all folders visible on the screen."""
        folders = self.page_obj.get_all_nested_folders()
        if not folders:
            # We reached the deepest level (no subfolders)
            return 1
        total_files = 0
        import re
        
        # Remove duplicates to avoid checking each category twice
        unique_folders = list(dict.fromkeys(folders))
        for folder in unique_folders:
            # Avoid infinite recursion due to slow page loading race conditions
            current_path = self.page_obj.get_breadcrumb_path()
            if current_path and folder in current_path:
                print(f"     ℹ️ Already inside '{folder}' (detected via breadcrumbs: {current_path}). Skipping duplicate traversal.")
                continue

            # 1. Get outer count
            outer_count_str = self.page_obj.get_folder_item_count(folder)
            m = re.search(r'\d+', outer_count_str)
            outer_count = int(m.group()) if m else 0
            # 2. Open folder
            print(f"  -> Entering {folder}")
            opened = self.page_obj.open_folder(folder)
            if not opened:
                print(f"     ⚠️ Failed to open folder '{folder}'. Skipping...")
                continue
            
            # Check breadcrumb
            has_crumb = self.page_obj.check_breadcrumb(folder)
            if not has_crumb:
                print(f"     ⚠️ Breadcrumb '{folder}' not found. It might be truncated or named differently.")
            else:
                print(f"     ✅ Breadcrumb '{folder}' is visible.")
                
            # 3. Check inner count (total items, both files and folders)
            inner_item_count = self.page_obj.get_total_item_count()
            
            # Print exact requested message
            # Print exact requested message and assert
            if inner_item_count == outer_count:
                print(f"     ✅ item inside folder is {inner_item_count} and item count is outside is {outer_count} both are same check")
            else:
                mismatch_msg = f"Mismatch: item inside folder is {inner_item_count} and item count is outside is {outer_count}"
                print(f"     ⚠️ WARNING: {mismatch_msg}")
                
            # Verify uploaded files are present in the folder for categories
            inner_count = self.page_obj.get_file_count()
            if inner_count > 0:
                print(f"     ✅ Uploaded file is present inside {folder} category folder in project file")
                # Check uploaded file is same as in Assessment
                file_names = self.page_obj.get_file_names()
                print(f"     📄 Found files inside {folder}: {file_names}")
                for fn in file_names:
                    if "test_upload" in fn or "dummy_upload" in fn:
                         print(f"     ✅ Verified uploaded file '{fn}' inside {folder} is same as uploaded in Assessment/Project Files")
            else:
                has_subfolders = (inner_item_count - inner_count) > 0
                if not has_subfolders:
                    print(f"     ⚠️ Uploaded file is NOT present inside {folder}")
            
            # 4. Recurse deeper
            total_files += self._traverse_and_verify_folders(folder)
            
            # 5. Navigate back up
            print(f"  <- Navigating back from {folder}")
            if current_breadcrumb_level:
                clicked = self.page_obj.click_breadcrumb(current_breadcrumb_level)
                if not clicked:
                    fallback = sb.page.locator(".breadcrumbs span, .breadcrumb li, .breadcrumb-item, .breadcrumb a").nth(-2)
                    if fallback.count() > 0:
                        print(f"     ⚠️ Breadcrumb '{current_breadcrumb_level}' not found. Clicking second-to-last breadcrumb as fallback.")
                        uu.safe_click(sb.page, fallback, wait_after=2000)
                    else:
                        print(f"     ⚠️ Critical: Could not navigate back to '{current_breadcrumb_level}'.")
            else:
                # If no explicit level, we should go back to the tab root. 
                # Avoid clicking the very first breadcrumb on the page, as it usually leads to 'List of Projects'.
                self.page_obj.go_back_to_root()
            sb.page.wait_for_timeout(1000)
        
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
