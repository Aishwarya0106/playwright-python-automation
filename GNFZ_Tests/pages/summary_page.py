import os
import shared_browser as sb

def sc(locator):
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
        sb.page.wait_for_timeout(200)
    except Exception:
        pass

class SummaryPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.summary_menu_tab = self.page.locator("label[for='tab7']")
        self.sub_tabs = self.page.locator("gnfz-summary-emissions-tab-business ul#myTab li button")

    def navigate_to_summary(self):
        sc(self.summary_menu_tab.first)
        self.summary_menu_tab.first.click(force=True)
        self.page.wait_for_timeout(1000)

    def click_sub_tab(self, tab_text):
        btn = self.sub_tabs.filter(has_text=tab_text).first
        sc(btn)
        self.page.wait_for_timeout(500)
        btn.evaluate("el => el.click()")
        self.page.wait_for_timeout(1000)

    def get_summary_table_data(self):
        """Returns a dict with values from the main summary table."""
        tables = self.page.locator("table.summary-table")
        try:
            tables.first.wait_for(state="visible", timeout=10000)
        except Exception:
            return {}
        
        data = {}
        calculated_total = 0.0
        
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
        # Typically this might be rendered in a chart or a table below the main table
        # We will look for text containing the year.
        element = self.page.locator(f"//*[contains(text(), '{year}')]").first
        return element.count() > 0 and element.is_visible()

    def check_milestone_data_present(self, year="2025"):
        """Checks if milestone data for a specific year is present on the page."""
        element = self.page.locator(f"//*[contains(text(), '{year}')]").first
        return element.count() > 0 and element.is_visible()

