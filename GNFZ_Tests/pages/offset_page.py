import os
import shared_browser as sb
from pages import ui_utils as uu

class OffsetPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.offset_menu_tab = self.page.locator("label[for='tab5']")
        self.sub_tabs = self.page.locator("gnfz-offset-tab ul#myTab li button")
        self.save_btn = self.page.locator("#gnfz-save")
        self.add_row_btn = self.page.locator("i.bi-plus-square")
        self.delete_row_btn = self.page.locator("i.bi-trash")
        self.toast_msg = self.page.locator(".toast-message, .ng-trigger-toastAnimation")

    def navigate_to_offset(self):
        uu.wait_for_page_stable(self.page)
        uu.safe_click(self.page, self.offset_menu_tab, wait_after=1000)

    def click_sub_tab(self, tab_text):
        btn = self.sub_tabs.filter(has_text=tab_text)
        uu.safe_click(self.page, btn, wait_after=1000)

    def get_active_panel(self):
        return self.page.locator("gnfz-offset-tab .tab-content > .tab-pane.active").first

    def add_row(self):
        panel = self.get_active_panel()
        self.page.wait_for_timeout(500)
        add_btn = panel.locator("i.bi-plus-square").last
        if add_btn.count() > 0:
            uu.safe_click(self.page, add_btn, wait_after=500)

    def delete_all_rows_except_first(self):
        panel = self.get_active_panel()
        self.page.wait_for_timeout(500)
        trash_btns = panel.locator("i.bi-trash")
        while trash_btns.count() > 1:
            btn = trash_btns.last
            uu.safe_click(self.page, btn, wait_after=500)

    def fill_date(self, row_index, date_str):
        panel = self.get_active_panel()
        inp = panel.locator("input.offset-datepicker").nth(row_index)
        try:
            inp.wait_for(state="attached", timeout=5000)
            uu.sc(inp)
            inp.evaluate("el => el.click()")
            self.page.wait_for_timeout(200)
            # Use evaluate to set value and dispatch events to guarantee Angular picks it up
            inp.evaluate(f"el => {{ el.value = '{date_str}'; el.dispatchEvent(new Event('input', {{bubbles: true}})); el.dispatchEvent(new Event('change', {{bubbles: true}})); }}")
            inp.press("Enter")
            self.page.wait_for_timeout(300)
        except Exception as e:
            print(f"Could not fill date for row {row_index}: {e}")

    def fill_values(self, row_index, planned_val, actual_val):
        panel = self.get_active_panel()
        p_inp = panel.locator("input[id^='offset_planned_']").nth(row_index)
        a_inp = panel.locator("input[id^='offset_actual_']").nth(row_index)
        
        try:
            p_inp.wait_for(state="attached", timeout=3000)
            uu.sc(p_inp)
            p_inp.fill(str(planned_val), force=True)
            p_inp.press("Enter")
            p_inp.press("Tab") # Trigger blur for cumulative calculation
        except: pass
            
        try:
            a_inp.wait_for(state="attached", timeout=3000)
            uu.sc(a_inp)
            a_inp.fill(str(actual_val), force=True)
            a_inp.press("Enter")
            a_inp.press("Tab") # Trigger blur for cumulative calculation
        except: pass
        self.page.wait_for_timeout(500)

    def upload_certificate(self, row_index):
        panel = self.get_active_panel()
        
        row = panel.locator(f"tr[id='records_{row_index}']").first
        if row.count() > 0:
            clip = row.locator("i.bi-paperclip")
            if clip.count() > 0:
                uu.safe_click(self.page, clip, wait_after=1500)
            
            file_input = self.page.locator("input[type='file']").first
            if file_input.count() > 0:
                upload_dir = r"C:\Users\Promantus\OneDrive\Desktop\files"
                os.makedirs(upload_dir, exist_ok=True)
                fpath = os.path.join(upload_dir, f"cert_dummy_{row_index}.txt")
                with open(fpath, "w") as f:
                    f.write("Offset Certificate Dummy")
                
                file_input.set_input_files(fpath)
                self.page.wait_for_timeout(1500)
                
                upload_btn = self.page.locator("button:has-text('Upload')").filter(has_text="Upload")
                if upload_btn.count() > 0:
                    uu.safe_click(self.page, upload_btn, wait_after=1000)
                    
                # Close panel if it remains open
                uu.close_blocking_modals(self.page)

    def click_save(self):
        btn = self.page.locator("gnfz-offset-tab #gnfz-save").first
        if btn.count() == 0:
            btn = self.page.locator("#gnfz-save").filter(state="visible").first
            
        if btn.count() > 0:
            uu.safe_click(self.page, btn, force=True, wait_after=200)

    def get_toast_message(self):
        try:
            self.toast_msg.first.wait_for(state="visible", timeout=5000)
            text = self.toast_msg.first.inner_text().strip()
            # Click toast to dismiss if possible
            try: uu.safe_click(self.page, self.toast_msg, wait_after=200)
            except Exception: pass
            return text
        except Exception:
            # Fallback: check for inline text-danger or invalid-feedback validation error
            try:
                err_locator = self.page.locator(".text-danger, .invalid-feedback, [class*='error'], .alert-danger, .swal2-html-container, .swal2-title, .toast-body")
                err_locator.first.wait_for(state="visible", timeout=3000)
                
                # If there are multiple errors, just return the first visible one
                for i in range(err_locator.count()):
                    if err_locator.nth(i).is_visible():
                        txt = err_locator.nth(i).inner_text().strip()
                        if txt: return txt
            except: pass
            return ""
