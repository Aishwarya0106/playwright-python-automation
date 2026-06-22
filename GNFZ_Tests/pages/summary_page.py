import os
import shared_browser as sb
from pages import ui_utils as uu

class SummaryPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.summary_menu_tab = self.page.locator("label[for='tab7']")
        self.sub_tabs = self.page.locator("ul#myTab li button, .nav-tabs li button")

    def navigate_to_summary(self):
        uu.wait_for_page_stable(self.page)
        uu.safe_click(self.page, self.summary_menu_tab, wait_after=1000)

    def click_sub_tab(self, tab_text):
        btn = self.sub_tabs.filter(has_text=tab_text).first
        uu.safe_click(self.page, btn, wait_after=1000)

    def get_summary_table_data(self):
        """Returns a dict with values from the main summary table."""
        # Ensure no modals are blocking before attempting to read data
        uu.close_blocking_modals(self.page)
        
        # Wait for any loading spinners to disappear
        spinners = self.page.locator(".spinner-border, ngx-spinner")
        if spinners.count() > 0:
            try:
                spinners.first.wait_for(state="hidden", timeout=15000)
            except Exception:
                pass
                
        # Locate all summary tables, but STRICTLY filter to only those currently visible on screen.
        # This prevents Playwright from finding a hidden table (e.g. in a closed modal or hidden sidebar)
        # and getting stuck waiting for it to become visible.
        tables = self.page.locator("table.summary-table").locator("visible=true")
            
        try:
            # Wait until at least one summary table matches the visible filter
            tables.first.wait_for(state="attached", timeout=15000)
            
            # Explicitly wait for rows to populate to avoid reading an empty table
            for _ in range(15):
                if tables.first.locator("tbody tr").count() > 0:
                    break
                self.page.wait_for_timeout(1000)
                
        except Exception as e:
            print(f"Warning: No visible summary table found: {e}")
            return {}
        
        data = {}
        calculated_total = 0.0
        
        # We only need one pass now that we've waited for rows
        for t_idx in range(tables.count()):
            table = tables.nth(t_idx)
            rows = table.locator("tbody tr")
            for i in range(rows.count()):
                row = rows.nth(i)
                text = row.inner_text().lower()
                cells = row.locator("td")
                if cells.count() >= 2:
                    # The first value column (KgCO2e, or energy unit)
                    val_text = cells.nth(1).inner_text().replace(',', '').strip()
                    if not val_text:
                        inp = cells.nth(1).locator("input").first
                        if inp.count() > 0:
                            val_text = inp.input_value().replace(',', '').strip()
                    
                    try:
                        val = float(val_text)
                        if "scope 1" in text:
                            data["scope 1"] = val
                        elif "scope 2" in text:
                            data["scope 2"] = val
                        elif "scope 3" in text:
                            data["scope 3"] = val
                        elif ("total emissions of the building" in text or "total" in text) and "avoided" not in text and "offset" not in text and "removal" not in text and "reduced" not in text and "milestone" not in text:
                            data["total"] = val
                        elif "emissions avoided by carbon offsets" in text or "carbon offsets" in text:
                            data["offsets"] = val
                        elif "emissions avoided by carbon removal strategies" in text or "carbon removal" in text:
                            data["removal"] = val
                        elif "emissions to be avoided" in text or "to be avoided" in text:
                            data["net_zero_avoided"] = val
                        elif "annual freshwater requirement" in text or "freshwater requirement" in text:
                            data["freshwater_requirement"] = val
                        elif "waste to be reduced" in text:
                            data["waste_reduced"] = val
                        
                        # Accumulate for calculated total if it's not a total or deduction row
                        if "total" not in text and "offset" not in text and "removal" not in text and "milestone" not in text and "avoided" not in text and "requirement" not in text and "reduced" not in text:
                            calculated_total += val
                    except ValueError:
                        pass
                            
        # If explicit total is 0 or missing, use the calculated total of the fields
        if "total" not in data or data["total"] == 0.0:
            data["total"] = calculated_total
            
        return data

    def check_offset_data_present(self, year="2026"):
        """Checks if offset data for a specific year is present on the page."""
        element = self.page.locator(f"//*[contains(text(), '{year}')]").first
        try:
            element.wait_for(state="attached", timeout=3000)
            return True
        except Exception:
            return False

    def check_milestone_data_present(self, year="2025"):
        """Checks if milestone data for a specific year is present on the page."""
        element = self.page.locator(f"//*[contains(text(), '{year}')]").first
        try:
            element.wait_for(state="attached", timeout=3000)
            return True
        except Exception:
            return False
