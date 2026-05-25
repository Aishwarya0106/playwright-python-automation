import os
import shared_browser as sb

def sc(locator):
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
        sb.page.wait_for_timeout(200)
    except Exception:
        pass

class NetZeroPlanPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.main_menu_tab = self.page.locator("#gnfz-nzp")
        self.main_menu_label = self.page.locator("label").filter(has_text="Net Zero Plan")
        self.panel_container = self.page.locator("gnfz-net-zero-plan-tab")
        self.sub_tab_buttons = self.page.locator("gnfz-net-zero-category-new-menu ul#myTab li button")
        self.tooltip_icon = self.panel_container.locator(".tooltipp i.bi-info-circle")
        self.tooltip_text = self.panel_container.locator(".tooltiptext")
        self.view_upload_btn = self.panel_container.locator("a:has-text('View/Upload')")
        
        self.file_panel = self.page.locator("#file-panel")
        self.active_status_title = self.page.locator("#activeStatusTitle")
        self.breadcrumbs = self.page.locator("gnfz-folder-container .breadcrumbs")
        self.add_files_btn = self.page.locator("#gnfz-files-add-more, a:has-text('Add files')")
        self.file_input = self.page.locator("input[type='file']")
        self.close_icon = self.page.locator("#process-status-close-change-event")

    def navigate_to_net_zero_plan(self):
        """Click the Net Zero Plan tab on the main navigation menu."""
        if self.main_menu_tab.count() > 0:
            self.main_menu_tab.locator("label").first.click(force=True)
        else:
            self.main_menu_label.first.click(force=True)
        self.page.wait_for_timeout(1000)
        self.page.wait_for_selector("gnfz-net-zero-plan-tab", timeout=15_000)

    def is_sub_tab_present(self, tab_name):
        """Check if a specific sub-tab exists."""
        return self.sub_tab_buttons.filter(has_text=tab_name).first.count() > 0

    def click_sub_tab(self, tab_name):
        """Click a sub-tab (e.g. 'Net Zero Emissions')."""
        self.sub_tab_buttons.filter(has_text=tab_name).first.click()
        self.page.wait_for_timeout(500)

    def get_tooltip_text(self):
        """Scroll to tooltip and get its text."""
        sc(self.tooltip_icon.first)
        icon = self.tooltip_icon.first
        # Wait for icon to be visible before hovering
        icon.wait_for(state='visible', timeout=10_000)
        icon.hover(force=True, timeout=15_000)
        self.page.wait_for_timeout(500)
        if self.tooltip_text.first.count() > 0:
            return self.tooltip_text.first.text_content().strip()
        return ""

    def click_view_upload(self):
        """Click View/Upload and wait for the file panel."""
        sc(self.view_upload_btn.first)
        btn = self.view_upload_btn.first
        # Wait for button to be visible and enabled before clicking
        btn.wait_for(state='visible', timeout=10_000)
        btn.click(timeout=15_000)
        self.page.wait_for_timeout(1500)
        self.page.wait_for_selector("#file-panel", timeout=15_000)

    def get_active_status_title(self):
        """Get the title shown in the file panel header."""
        if self.active_status_title.first.count() > 0:
            return self.active_status_title.first.inner_text().strip()
        return ""

    def get_breadcrumbs_text(self):
        """Get the full breadcrumb trail text."""
        if self.breadcrumbs.first.count() > 0:
            return self.breadcrumbs.first.inner_text().strip()
        return ""

    def upload_dummy_file(self):
        """Create a dummy file and upload it using the Add files button."""
        upload_dir = r"C:\Users\Promantus\OneDrive\Desktop\files"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, "net_zero_plan_test.txt")
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("Net Zero Plan Dummy Upload")
        
        add_btn = self.add_files_btn.first
        if add_btn.count() > 0 and add_btn.is_visible():
            add_btn.click()
            self.page.wait_for_timeout(500)
            
            f_input = self.file_input.first
            if f_input.count() > 0:
                f_input.set_input_files(file_path)
                self.page.wait_for_timeout(1500)
                return True
        return False

    def close_file_panel(self):
        """Close the file upload panel."""
        icon = self.close_icon.first
        if icon.count() > 0 and icon.is_visible():
            icon.click()
            self.page.wait_for_timeout(1000)
