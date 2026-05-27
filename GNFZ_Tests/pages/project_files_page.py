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
        tab_id = f"#gnfz-{tab_name}"
        btn = self.page.locator(tab_id).first
        if btn.count() > 0:
            uu.safe_click(self.page, btn, wait_after=1000)
            return True
        return False

    def get_all_nested_folders(self):
        """Returns a list of folder names currently visible in the active side tab."""
        for _ in range(10):
            if self.page.locator("tr#files").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        folders = []
        # Usually folders have bi-folder-fill icon
        folder_elements = self.page.locator("tr#files td:has(i.bi-folder-fill) .gnfz-file-name-ellipsis")
        for i in range(folder_elements.count()):
            folders.append(folder_elements.nth(i).inner_text().strip())
        return folders

    def open_folder(self, folder_name):
        """Clicks a folder to open it."""
        folder_link = self.page.locator(f"tr#files td:has(i.bi-folder-fill) .gnfz-file-name-ellipsis:has-text('{folder_name}')").first
        if folder_link.count() > 0:
            uu.safe_click(self.page, folder_link, wait_after=1000)
            return True
        return False

    def go_back_to_root(self):
        """Clicks the root breadcrumb to go back."""
        # Typically the root breadcrumb is 'Files' or similar
        breadcrumb = self.page.locator(".breadcrumbs span:has-text('Files'), .breadcrumb li:has-text('Files')").first
        if breadcrumb.count() > 0:
            uu.safe_click(self.page, breadcrumb, wait_after=500)

    def check_breadcrumb(self, name):
        """Checks if a breadcrumb with the given name is present."""
        breadcrumb = self.page.locator(f".breadcrumbs span:has-text('{name}'), .breadcrumb li:has-text('{name}'), .breadcrumb-item:has-text('{name}')").first
        if breadcrumb.count() == 0:
            breadcrumb = self.page.locator(f"a:has-text('{name}'), span:text-is('{name}')").first
        return breadcrumb.count() > 0 and breadcrumb.is_visible()

    def click_breadcrumb(self, name):
        """Clicks a breadcrumb with the given name."""
        breadcrumb = self.page.locator(f".breadcrumbs span:has-text('{name}'), .breadcrumb li:has-text('{name}'), .breadcrumb-item:has-text('{name}')").first
        if breadcrumb.count() == 0:
            breadcrumb = self.page.locator(f"a:has-text('{name}'), span:text-is('{name}')").first
        if breadcrumb.count() > 0:
            uu.safe_click(self.page, breadcrumb, wait_after=2000)
            return True
        return False

    def get_file_count(self):
        """Returns the number of files (not folders) currently displayed."""
        for _ in range(10):
            if self.page.locator("tr#files").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        all_rows = self.page.locator("tr#files")
        folder_rows = self.page.locator("tr#files:has(i.bi-folder-fill)")
        return all_rows.count() - folder_rows.count()

    def get_total_item_count(self):
        """Returns the total number of items (files + folders) currently displayed."""
        for _ in range(10):
            if self.page.locator("tr#files").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        return self.page.locator("tr#files").count()

    def get_file_names(self):
        """Returns the names of the files in the current folder."""
        for _ in range(10):
            if self.page.locator("tr#files").count() > 0 or self.check_no_records_found():
                break
            self.page.wait_for_timeout(500)
        self.page.wait_for_timeout(500)
        file_names = []
        file_rows = self.page.locator("tr#files:not(:has(i.bi-folder-fill)) .gnfz-file-name-ellipsis")
        for i in range(file_rows.count()):
            file_names.append(file_rows.nth(i).inner_text().strip())
        return file_names

    def get_folder_item_count(self, folder_name):
        """Returns the item count string (e.g. '0 items') shown next to a folder in the root view."""
        row = self.page.locator(f"tr#files:has(.gnfz-file-name-ellipsis:has-text('{folder_name}'))").first
        if row.count() > 0:
            # The item count is usually in the 3rd td
            tds = row.locator("td.text-end.text-secondary")
            if tds.count() > 0:
                return tds.first.inner_text().strip()
        return ""

    def check_no_records_found(self):
        """Checks if 'No records found' or 'No files' message is displayed inside a folder."""
        # Typically represented by a specific div or table cell
        no_records = self.page.locator("text='No records found', text='No items found', text='0 items'").first
        return no_records.count() > 0 and no_records.is_visible()

    def upload_file(self, file_name="dummy_upload.txt"):
        """Uploads a file using the 'Add Files' mechanism."""
        # Let's try to find an 'Add Files' button or an input[type='file']
        add_files_btn = self.page.locator("a#gnfz-files-add-more, a:has-text('Add files'), button:has-text('Add Files'), .bi-upload, [title*='Upload'], [title*='Add File']").first
        
        # If we can click an upload button
        if add_files_btn.count() > 0 and add_files_btn.is_visible():
            uu.safe_click(self.page, add_files_btn, wait_after=1000)
            
        file_input = self.page.locator("input#file-uploader-scope, input[type='file']").first
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
            if upload_confirm_btn.count() > 0 and upload_confirm_btn.is_visible():
                uu.safe_click(self.page, upload_confirm_btn, wait_after=2000)
            
            # Close modal if present
            uu.close_blocking_modals(self.page)
            
            return True
        return False
