import os
import shared_browser as sb
from pages import ui_utils as uu

class ProjectFilesPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.project_files_menu_tab = self.page.locator("label[for='tab8']")
        self.side_tabs_container = self.page.locator("#menu-upload-list ul")
        
    def navigate_to_project_files(self):
        uu.wait_for_page_stable(self.page)
        uu.safe_click(self.page, self.project_files_menu_tab, wait_after=1000)

    def click_side_tab(self, tab_name):
        # The id of side tabs are like "gnfz-Building Info", "gnfz-Assessment", etc.
        # Use attribute selector [id='...'] to safely handle spaces in tab_name
        btn = self.page.locator(f"[id='gnfz-{tab_name}']").first
        if btn.count() > 0:
            uu.safe_click(self.page, btn, wait_after=1000)
            return True
        return False

    def get_all_nested_folders(self):
        """Returns a list of folder names currently visible in the active side tab."""
        for _ in range(10):
            # Wait for any file/folder rows to appear or an empty state
            if self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        folders = []
        # Usually folders have bi-folder-fill icon; use flexible row selector
        folder_elements = self.page.locator("tr:has(i.bi-folder-fill) .gnfz-file-name-ellipsis")
        for i in range(folder_elements.count()):
            folders.append(folder_elements.nth(i).inner_text().strip())
        return folders

    def open_folder(self, folder_name):
        """Clicks a folder to open it."""
        safe_name = folder_name.replace("'", "\\'")
        
        # Use XPath with normalize-space to match exact name regardless of surrounding whitespace/tabs
        xpath_sel = f"xpath=//tr[descendant::*[contains(@class, 'gnfz-file-name-ellipsis') and normalize-space(.)='{safe_name}']]"
        folder_row = self.page.locator(xpath_sel).first
        
        # Wait up to 10 seconds for the specific folder row to be attached to DOM
        try:
            folder_row.wait_for(state="attached", timeout=10000)
        except Exception:
            # Fallback wait with CSS has-text
            fallback_row = self.page.locator(f"tr:has(.gnfz-file-name-ellipsis:has-text('{safe_name}'))").first
            try:
                fallback_row.wait_for(state="attached", timeout=5000)
            except Exception:
                pass
            
        # Re-resolve after waiting
        folder_row = self.page.locator(xpath_sel).first
        if folder_row.count() == 0:
            folder_row = self.page.locator(f"tr:has(.gnfz-file-name-ellipsis:text-is('{safe_name}'))").first
        if folder_row.count() == 0:
            folder_row = self.page.locator(f"tr:has(.gnfz-file-name-ellipsis:has-text('{safe_name}'))").first
            
        if folder_row.count() > 0:
            ellipsis = folder_row.locator(".gnfz-file-name-ellipsis").first
            if ellipsis.count() == 0:
                ellipsis = folder_row.locator("span, a, td").first
                
            try:
                # Try clicking the text ellipsis first as it's the standard Angular target
                uu.safe_click(self.page, ellipsis, wait_after=1000)
            except Exception as e:
                print(f"      ⚠️ Standard click failed: {e}. Trying JS click on ellipsis...")
                try:
                    # Fallback 1: JS click on ellipsis
                    ellipsis.evaluate("el => el.click()")
                    self.page.wait_for_timeout(1000)
                except Exception as e2:
                    print(f"      ⚠️ JS click on ellipsis failed: {e2}. Trying row click...")
                    try:
                        # Fallback 2: Try clicking the row itself
                        uu.safe_click(self.page, folder_row, wait_after=1000)
                    except Exception as e3:
                        print(f"      ⚠️ Row click failed: {e3}. Trying JS click on row...")
                        # Fallback 3: Evaluate JS click on row
                        folder_row.evaluate("el => el.click()")
            
            # Verify if the folder actually opened by checking the breadcrumb within an extended window (10 seconds)
            opened = False
            for _ in range(20):
                if self.check_breadcrumb(folder_name):
                    opened = True
                    break
                self.page.wait_for_timeout(500)
                
            if not opened:
                print(f"     ⚠️ Breadcrumb for '{folder_name}' not found after click. Folder failed to open.")
                return False
                
            # Wait for the clicked folder row to disappear from the DOM (meaning we navigated inside)
            try:
                folder_row.wait_for(state="hidden", timeout=5000)
            except Exception:
                pass
                
            return True
        return False

    def go_back_to_root(self):
        """Clicks the root breadcrumb to go back."""
        # Typically the root breadcrumb is 'Files' or similar
        breadcrumb = self.page.locator(".breadcrumbs span:has-text('Files'), .breadcrumb li:has-text('Files')").first
        if breadcrumb.count() > 0:
            uu.safe_click(self.page, breadcrumb, wait_after=500)

    def get_breadcrumb_path(self):
        """Return the visible breadcrumb trail as a list of labels."""
        breadcrumb_items = self.page.locator(".breadcrumbs span, .breadcrumb li, .breadcrumb-item, .breadcrumb a")
        path = []
        for raw in breadcrumb_items.all_inner_texts():
            item = raw.strip()
            if not item:
                continue
            # Remove common separators that may appear in breadcrumb text
            for part in [p.strip() for p in item.replace('»', '>').split('>') if p.strip()]:
                if part not in ['/', '>', '|', '»']:
                    path.append(part)
        return path

    def click_parent_breadcrumb(self):
        """Clicks the immediate parent breadcrumb entry to navigate one level up."""
        path = self.get_breadcrumb_path()
        if len(path) < 2:
            return False

        parent_name = path[-2]
        return self.click_breadcrumb(parent_name)

    def check_breadcrumb(self, name):
        """Checks if a breadcrumb with the given name is present."""
        safe_name = name.replace("'", "\\'")
        # XPath with normalize-space to handle any spacing variations
        xpath_sel = f"xpath=//*[self::span or self::li or self::a][contains(@class, 'breadcrumb') or ancestor::*[contains(@class, 'breadcrumb')]][normalize-space(.)='{safe_name}']"
        breadcrumb = self.page.locator(xpath_sel).first
        if breadcrumb.count() > 0 and breadcrumb.is_visible():
            return True
            
        # Standard exact locators
        breadcrumb = self.page.locator(
            f".breadcrumbs span:text-is('{name}'), .breadcrumbs a:text-is('{name}'), .breadcrumb li:text-is('{name}'), .breadcrumb-item:text-is('{name}'), .breadcrumb a:text-is('{name}')"
        ).first
        if breadcrumb.count() > 0 and breadcrumb.is_visible():
            return True
            
        # Standard substring locators
        breadcrumb = self.page.locator(
            f".breadcrumbs span:has-text('{name}'), .breadcrumbs a:has-text('{name}'), .breadcrumb li:has-text('{name}'), .breadcrumb-item:has-text('{name}'), .breadcrumb a:has-text('{name}')"
        ).first
        if breadcrumb.count() > 0 and breadcrumb.is_visible():
            return True
            
        # Truncation fallback: check for prefix match if name is long
        if len(name) > 8:
            prefix = name[:8]
            breadcrumb = self.page.locator(
                f".breadcrumbs span:has-text('{prefix}'), .breadcrumbs a:has-text('{prefix}'), .breadcrumb li:has-text('{prefix}'), .breadcrumb-item:has-text('{prefix}'), .breadcrumb a:has-text('{prefix}')"
            ).first
            if breadcrumb.count() > 0 and breadcrumb.is_visible():
                print(f"      ℹ️ Breadcrumb matched truncated/prefix: '{prefix}' for '{name}'")
                return True
                
        return False

    def click_breadcrumb(self, name):
        """Clicks a breadcrumb with the given name."""
        safe_name = name.replace("'", "\\'")
        # XPath with normalize-space first
        xpath_sel = f"xpath=//*[self::span or self::li or self::a][contains(@class, 'breadcrumb') or ancestor::*[contains(@class, 'breadcrumb')]][normalize-space(.)='{safe_name}']"
        breadcrumb = self.page.locator(xpath_sel).first
        
        if breadcrumb.count() == 0:
            breadcrumb = self.page.locator(f".breadcrumbs span:text-is('{safe_name}'), .breadcrumbs a:text-is('{safe_name}'), .breadcrumb li:text-is('{safe_name}'), .breadcrumb-item:text-is('{safe_name}')").first
        if breadcrumb.count() == 0:
            breadcrumb = self.page.locator(f".breadcrumbs span:has-text('{safe_name}'), .breadcrumbs a:has-text('{safe_name}'), .breadcrumb li:has-text('{safe_name}'), .breadcrumb-item:has-text('{safe_name}')").first
            
        # Try truncated prefix match if name is long
        if breadcrumb.count() == 0 and len(name) > 8:
            prefix = name[:8]
            breadcrumb = self.page.locator(f".breadcrumbs span:has-text('{prefix}'), .breadcrumbs a:has-text('{prefix}'), .breadcrumb li:has-text('{prefix}'), .breadcrumb-item:has-text('{prefix}')").first
            
        if breadcrumb.count() > 0:
            uu.safe_click(self.page, breadcrumb, wait_after=2000)
            return True
        return False

    def get_file_count(self, expected_total=None):
        """Returns the number of files (not folders) currently displayed."""
        self.get_total_item_count(expected_total) # wait for DOM to stabilize based on expected count
        all_rows = self.page.locator("tr:has(.gnfz-file-name-ellipsis)")
        folder_rows = self.page.locator("tr:has(i.bi-folder-fill)")
        return max(0, all_rows.count() - folder_rows.count())

    def get_total_item_count(self, expected_count=None):
        """Returns the total number of items (files + folders) currently displayed.
        If expected_count is provided, it polls until that exact count is met to bypass flashing empty states."""
        
        # If we expect a specific count, poll until we see exactly that many items
        if expected_count is not None and expected_count > 0:
            for _ in range(15):
                # Count rows in the visible file table
                current_count = self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count()
                if current_count == expected_count:
                    return current_count
                self.page.wait_for_timeout(1000)
            return self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count()
            
        # If expected_count is 0 or None, use standard stable logic
        for _ in range(15):
            current_count = self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count()
            if current_count > 0:
                # If we expect 0 but found some, return them immediately
                if expected_count == 0:
                    return current_count
                # If no expected count, return what we found but wait a bit to ensure it's not still rendering
                self.page.wait_for_timeout(500)
                return self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count()
                
            if self.check_no_records_found(stable_wait=True):
                return 0
            self.page.wait_for_timeout(1000)
            
        return self.page.locator("tr:has(.gnfz-file-name-ellipsis)").count()

    def get_file_names(self):
        """Returns the names of the files in the current folder."""
        for _ in range(10):
            if self.page.locator("tr#files").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        file_names = []
        file_rows = self.page.locator("tr:has(.gnfz-file-name-ellipsis):not(:has(i.bi-folder-fill)) .gnfz-file-name-ellipsis")
        for i in range(file_rows.count()):
            file_names.append(file_rows.nth(i).inner_text().strip())
        return file_names

    def get_folder_item_count(self, folder_name):
        """Returns the item count string (e.g. '0 items') shown next to a folder in the root view."""
        safe_name = folder_name.replace("'", "\\'")
        xpath_sel = f"xpath=//tr[descendant::*[contains(@class, 'gnfz-file-name-ellipsis') and normalize-space(.)='{safe_name}']]"
        row = self.page.locator(xpath_sel).first
        
        if row.count() == 0:
            row = self.page.locator(f"tr:has(.gnfz-file-name-ellipsis:text-is('{safe_name}'))").first
        if row.count() == 0:
            row = self.page.locator(f"tr:has(.gnfz-file-name-ellipsis:has-text('{safe_name}'))").first
            
        if row.count() > 0:
            # The item count is usually in the 3rd td
            tds = row.locator("td.text-end.text-secondary")
            if tds.count() > 0:
                return tds.first.inner_text().strip()
        return ""

    def check_no_records_found(self, stable_wait=False):
        """Checks if 'No records found' or 'No files' message is displayed inside a folder."""
        # Use XPath to safely find empty state messages without CSS parsing limitations
        no_records = self.page.locator("xpath=//*[self::td or self::div or self::span or self::p][contains(text(), 'No records found') or contains(text(), 'No items found') or contains(text(), 'No files found')]").first
        
        # If stable_wait is True, we ensure the message stays on screen for a moment
        # to avoid false positives during Angular component re-renders
        if stable_wait:
            if no_records.count() > 0 and no_records.is_visible():
                self.page.wait_for_timeout(1000) # Wait to see if it's just a flash
                if no_records.count() > 0 and no_records.is_visible() and self.page.locator("tr#files").count() == 0:
                    return True
            return False
            
        return no_records.count() > 0 and no_records.is_visible()

    def upload_file(self, file_name="dummy_upload.txt"):
        """Uploads a file using the 'Add Files' mechanism."""
        # Let's try to find an 'Add Files' button or an input[type='file']
        add_files_btn = self.page.locator("a#gnfz-files-add-more, a:has-text('Add files'), button:has-text('Add Files'), .bi-upload, [title*='Upload'], [title*='Add File']").first
        
        # If we can click an upload button
        if add_files_btn.count() > 0 and add_files_btn.is_visible():
            uu.safe_click(self.page, add_files_btn, wait_after=1000)
            
        file_input = self.page.locator("input#file-uploader-scope, input[type='file']").first
        try:
            file_input.wait_for(state="attached", timeout=5000)
        except Exception:
            pass
            
        if file_input.count() > 0:
            upload_dir = r"C:\Users\Promantus\OneDrive\Desktop\files"
            os.makedirs(upload_dir, exist_ok=True)
            fpath = os.path.join(upload_dir, file_name)
            with open(fpath, "w") as f:
                f.write(f"This is a test file: {file_name}")
            
            file_input.set_input_files(fpath)
            self.page.wait_for_timeout(2000)
            
            # If there's an 'Upload' confirmation button in a modal
            upload_confirm_btn = self.page.locator("button:has-text('Upload')").filter(has_text="Upload").first
            try:
                upload_confirm_btn.wait_for(state="visible", timeout=3000)
                uu.safe_click(self.page, upload_confirm_btn, wait_after=2000)
            except Exception:
                pass
            
            # If there is a Close/generic modal close button, let's close it too
            close_btn = self.page.locator("#modal-generic-close, .modal.show .btn-close, .modal.show .close").first
            if close_btn.count() > 0 and close_btn.is_visible():
                uu.safe_click(self.page, close_btn, wait_after=1000)
            
            # Close modal if present
            uu.close_blocking_modals(self.page)
            
            return True
        return False
