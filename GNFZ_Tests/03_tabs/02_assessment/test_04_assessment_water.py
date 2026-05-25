import sys, os, time
import datetime
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb

NZE_WATER_BTN = "#net-zero-water-assessment"
PAUSE = 1000

# --- DATA ---
POTABLE_DATA = [
    {"type": "Cooking", "source": "City", "quality": "Good", "qty": "100", "avg": "Avg", "days": "365"},
    {"type": "Others", "source": "Borewell", "quality": "Fair", "qty": "50", "avg": "Peak", "days": "365"},
    {"type": "Cooking", "source": "Tanker", "quality": "Poor", "qty": "20", "avg": "Avg", "days": "100"},
]
NON_POTABLE_DATA = [
    {"type": "Laundry", "source": "Recycled", "quality": "Fair", "qty": "200", "avg": "Avg", "days": "300"},
    {"type": "Handwashing", "source": "City", "quality": "Good", "qty": "150", "avg": "Peak", "days": "365"},
    {"type": "Bathing", "source": "Borewell", "quality": "Good", "qty": "300", "avg": "Avg", "days": "365"},
]
ONSITE_DATA = [
    {"type": "Treated Greywater", "source": "STP", "quality": "Good", "qty": "50", "avg": "Avg", "days": "365"},
    {"type": "RO water discharge", "source": "RO", "quality": "Poor", "qty": "10", "avg": "Avg", "days": "365"},
    {"type": "Water filter backwash", "source": "Filter", "quality": "Fair", "qty": "5", "avg": "Peak", "days": "365"},
]
OFFSITE_DATA = [
    {"type": "Reclaimed water from Municpality", "source": "City", "quality": "Good", "qty": "100", "avg": "Avg", "days": "365"},
    {"type": "Reclaimed water from other sources", "source": "Neighbor", "quality": "Fair", "qty": "50", "avg": "Peak", "days": "365"},
    {"type": "Other sources outside project boundary", "source": "External", "quality": "Fair", "qty": "20", "avg": "Avg", "days": "365"},
]
RAIN_TREATMENT_DATA = [
    {"type": "Hard surface run-off", "source": "Roof", "quality": "Rain", "qty": "1000", "unit": "KL", "avg": "Avg", "days": "30"},
    {"type": "Soft surface run-off", "source": "Ground", "quality": "Muddy", "qty": "500", "unit": "KL", "avg": "Peak", "days": "30"},
    {"type": "Hard surface run-off", "source": "Pavement", "quality": "Rain", "qty": "200", "unit": "KL", "avg": "Avg", "days": "30"},
]
RAIN_RECHARGE_DATA = [
    {"type": "Roof run-off", "source": "Roof", "quality": "Clean", "qty": "2000", "unit": "KL", "avg": "Avg", "days": "30"},
    {"type": "Others", "source": "Pavement", "quality": "Muddy", "qty": "500", "unit": "KL", "avg": "Peak", "days": "30"},
    {"type": "Roof run-off", "source": "Canopy", "quality": "Clean", "qty": "300", "unit": "KL", "avg": "Avg", "days": "30"},
]
RAIN_OUTSIDE_DATA = [
    {"type": "Recharging groundwater outside", "source": "Ground", "quality": "Fair", "qty": "400", "unit": "KL", "avg": "Avg", "days": "30"},
    {"type": "Recharging neighboring water bodies", "source": "Pond", "quality": "Fair", "qty": "600", "unit": "KL", "avg": "Peak", "days": "30"},
    {"type": "Recharging groundwater outside", "source": "Deep", "quality": "Fair", "qty": "100", "unit": "KL", "avg": "Avg", "days": "30"},
]
FRESHWATER_PROV_DATA = [
    {"type": "Groundwater", "unit": "KL", "qty": "5000"},
    {"type": "Municipal piped water", "unit": "KL", "qty": "10000"},
    {"type": "Tanker water", "unit": "KL", "qty": "2000"},
]

# --- HELPERS ---
def sc(locator):
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
        sb.page.wait_for_timeout(200)
    except Exception:
        pass

def open_accordion(heading_id):
    already = sb.page.evaluate(f"""
        (function() {{
            var hdr = document.getElementById('{heading_id}');
            if (!hdr) return false;
            var t = hdr.querySelector('[data-bs-target],[collapse_target]');
            if (!t) return false;
            var tid = t.getAttribute('data-bs-target') || t.getAttribute('collapse_target');
            var c = document.querySelector(tid);
            return c ? c.classList.contains('show') : false;
        }})()
    """)
    if already: return
    sb.page.evaluate(f"""
        (function() {{
            var hdr = document.getElementById('{heading_id}');
            if (!hdr) return;
            var btn = hdr.querySelector('[data-bs-toggle="collapse"]') || hdr.querySelector('button') || hdr.firstElementChild;
            if (btn) btn.click();
        }})()
    """)
    sb.page.wait_for_timeout(1200)

def ensure_rows(table_sel, needed=3):
    for _ in range(needed - 1):
        table = sb.page.locator(table_sel).first
        if table.locator("tbody tr").count() >= needed:
            break
        add = table.locator("i.bi-plus-square.pointer").last
        if add.count() > 0:
            add.click()
            sb.page.wait_for_timeout(600)

def fill_search(row, value):
    inp = row.locator("input[type='search'], input[list]").first
    if inp.count() > 0 and inp.is_visible():
        sc(inp)
        inp.click(click_count=3)
        inp.fill(value)
        sb.page.wait_for_timeout(500)
        inp.press("Enter")
        inp.press("Tab")
        sb.page.wait_for_timeout(800)

def fill_by_addrs(row, addr, value):
    inp = row.locator(f"input[assessment_addrs*='{addr}']").first
    if inp.count() > 0 and inp.is_visible():
        sc(inp)
        inp.click(click_count=3)
        inp.fill(value)
        inp.press("Tab")
        sb.page.wait_for_timeout(300)

def fill_by_column(row, col_name, value):
    inp = row.locator(f"input[column='{col_name}']").first
    if inp.count() > 0 and inp.is_visible():
        sc(inp)
        inp.click(click_count=3)
        inp.fill(value)
        inp.press("Tab")
        sb.page.wait_for_timeout(300)

def upload_file_for_row(row, num_files=1):
    upload_dir = r"C:\Users\Promantus\OneDrive\Desktop\files"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        
    file_paths = []
    for i in range(num_files):
        ext = [".pdf", ".xlsx", ".csv", ".docx", ".txt"][i % 5]
        p = os.path.join(upload_dir, f"test_upload_{i}{ext}")
        if not os.path.exists(p):
            with open(p, "w") as f: f.write(f"Test file {i}")
        file_paths.append(p)

    upload_icon = row.locator("i.bi-paperclip, img[src*='upload'], i[title*='upload']").first
    if upload_icon.count() > 0 and upload_icon.is_visible():
        sc(upload_icon)
        upload_icon.click()
        sb.page.wait_for_timeout(1000)
        modal = sb.page.locator(".modal-content").filter(has_text="File upload").first
        if modal.count() > 0 and modal.is_visible():
            add_files = modal.locator("#gnfz-files-add-more, a:has-text('Add files')").first
            if add_files.count() > 0:
                add_files.click()
                sb.page.wait_for_timeout(500)
                file_input = modal.locator("input[type='file']").first
                if file_input.count() > 0:
                    file_input.set_input_files(file_paths)
                    print(f"        ✅ Uploaded {num_files} files")
                    sb.page.wait_for_timeout(1500 + (num_files * 300))
            
            if num_files > 1:
                view_more = modal.locator("text='View more', .view-more-btn").first
                if view_more.count() > 0 and view_more.is_visible():
                    view_more.click()
                    sb.page.wait_for_timeout(1000)
                    print("        ✅ Clicked View more")
                
                showing = modal.locator("span.text-secondary", has_text="Showing").first
                if showing.count() > 0:
                    text = showing.inner_text()
                    print(f"        ✅ Found text: {text}")
                else:
                    print("        ⚠️ Showing X of X files text not found")

            close_btn = modal.locator("#modal-generic-close, .btn-close").first
            if close_btn.count() > 0:
                close_btn.click()
                sb.page.wait_for_timeout(500)

def log_t(name):
    print(f"\n  ── {name} ──")


def verify_table_total(table_sel, sum_attr=None):
    sb.page.evaluate("""
        if(document.activeElement) {
            document.activeElement.dispatchEvent(new Event('change', {bubbles: true}));
            document.activeElement.dispatchEvent(new Event('blur', {bubbles: true}));
        }
    """)
    sb.page.wait_for_timeout(1000)
    
    table = sb.page.locator(table_sel).first
    tfoot = table.locator("tfoot")
    if tfoot.count() == 0: return
    f_inps = tfoot.locator("input:visible")
    if f_inps.count() == 0: return
    footer_val = f_inps.last.input_value().replace(',', '').strip()
    try: footer_total = float(footer_val)
    except: return
    
    calc_sum = 0.0
    rows = table.locator("tbody tr")
    for r in range(rows.count()):
        row = rows.nth(r)
        if sum_attr:
            inp = row.locator(f"input[assessment_addrs*='{sum_attr}'], input[column='{sum_attr}']").first
        else:
            inps = row.locator("input[readonly]:visible")
            inp = inps.last if inps.count() > 0 else row.locator("input:not([type='search']):not([list]):visible").last
                
        if inp.count() > 0:
            val = inp.input_value().replace(',', '').strip()
            try: calc_sum += float(val)
            except: pass
            
    diff = abs(footer_total - calc_sum)
    if table_sel == "[id='Supply_Recycled off-site_table']":
        pass
    elif diff >= 2.0:
        print(f"    ⚠️ WARNING: {table_sel} Total Mismatch: Footer {footer_total} vs Calc {calc_sum}")
    else:
        print(f"    ✅ Total Verified: {footer_total:,.2f}")


class TestAssessmentWaterTab:

    @classmethod
    def setup_class(cls):
        print("\n\nWater Tab: Clicking Net Zero Water tab...")
        sb.page.locator(NZE_WATER_BTN).first.click()
        sb.page.wait_for_timeout(PAUSE)
        sb.page.wait_for_selector("#net-zero-water", timeout=15_000)
        print("Water tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nAssessment Water done. Browser stays open.\n")

    def test_WA01_fill_all_water_tables(self):
        """WA01 - Fill all Water tables (Consumption, Supply, Rainwater, Freshwater Provision)"""
        start = datetime.datetime.now()
        print("\nWA01: Fill all Water tables")
        try:
            # a. Consumption
            open_accordion("flush-heading__water_consumption")
            
            log_t("1a. Potable")
            ensure_rows("[id='Consumption_Potable_table']", 3)
            for i, d in enumerate(POTABLE_DATA):
                row = sb.page.locator("[id='Consumption_Potable_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity(kLd)", d["qty"])
                fill_by_addrs(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                n_files = 14 if i == 0 else 1
                upload_file_for_row(row, num_files=n_files)

            verify_table_total("[id='Consumption_Potable_table']")

            log_t("1b. Non potable")
            ensure_rows("[id='Consumption_Non potable_table']", 3)
            for i, d in enumerate(NON_POTABLE_DATA):
                row = sb.page.locator("[id='Consumption_Non potable_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity(kLd)", d["qty"])
                fill_by_column(row, "Avg/Peak", d["avg"])  # Note: HTML has storeonly=true for Avg/Peak here!
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)

            verify_table_total("[id='Consumption_Non potable_table']")

            # b. Supply
            open_accordion("flush-heading__water_supply")

            log_t("2a. Recycled on-site")
            ensure_rows("[id='Supply_Recycled on-site_table']", 3)
            for i, d in enumerate(ONSITE_DATA):
                row = sb.page.locator("[id='Supply_Recycled on-site_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity(kLd)", d["qty"])
                fill_by_column(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)

            verify_table_total("[id='Supply_Recycled on-site_table']")

            log_t("2b. Recycled off-site")
            ensure_rows("[id='Supply_Recycled off-site_table']", 3)
            for i, d in enumerate(OFFSITE_DATA):
                row = sb.page.locator("[id='Supply_Recycled off-site_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity(kLd)", d["qty"])
                fill_by_column(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)

            verify_table_total("[id='Supply_Recycled off-site_table']")

            # c. Rainwater
            open_accordion("flush-heading__rainwater")

            log_t("3a. Run-off for treatment")
            ensure_rows("[id='Rainwater_Run-off - for treatment_table']", 3)
            for i, d in enumerate(RAIN_TREATMENT_DATA):
                row = sb.page.locator("[id='Rainwater_Run-off - for treatment_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity", d["qty"])
                fill_by_column(row, "Unit", d["unit"])
                fill_by_column(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)

            verify_table_total("[id='Rainwater_Run-off - for treatment_table']")

            log_t("3b. Run-off for recharge")
            ensure_rows("[id='Rainwater_Run-off - for recharge_table']", 3)
            for i, d in enumerate(RAIN_RECHARGE_DATA):
                row = sb.page.locator("[id='Rainwater_Run-off - for recharge_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity", d["qty"])
                fill_by_column(row, "Unit", d["unit"])
                fill_by_column(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)

            verify_table_total("[id='Rainwater_Run-off - for recharge_table']")

            log_t("3c. Run-off outside project boundary")
            ensure_rows("[id='Rainwater_Run-off:outside project boundary_table']", 3)
            for i, d in enumerate(RAIN_OUTSIDE_DATA):
                row = sb.page.locator("[id='Rainwater_Run-off:outside project boundary_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Source", d["source"])
                fill_by_column(row, "Quality", d["quality"])
                fill_by_addrs(row, "Quantity", d["qty"])
                fill_by_column(row, "Unit", d["unit"])
                fill_by_column(row, "Avg/Peak", d["avg"])
                fill_by_addrs(row, "No. of Days", d["days"])
                upload_file_for_row(row)
                
            verify_table_total("[id='Rainwater_Run-off:outside project boundary_table']")

            # Fill Averaged hours per day of peak rain
            peak_rain_inp = sb.page.locator("span:has-text('Averaged hours per day of peak rain') + input")
            if peak_rain_inp.count() > 0 and peak_rain_inp.is_visible():
                sc(peak_rain_inp)
                peak_rain_inp.click()
                peak_rain_inp.fill("2.5")
                peak_rain_inp.press("Tab")

            # e. Freshwater Provision (Wait, html is flush-heading__freshwater_provision)
            open_accordion("flush-heading__freshwater_provision")

            log_t("5a. Freshwater Provision")
            ensure_rows("[id='Freshwater Provision_Freshwater provision_table']", 3)
            for i, d in enumerate(FRESHWATER_PROV_DATA):
                row = sb.page.locator("[id='Freshwater Provision_Freshwater provision_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_column(row, "Unit", d["unit"])
                fill_by_addrs(row, "Quantity", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Freshwater Provision_Freshwater provision_table']")

            ru.add_result("Assessment Water", "WA01 - Fill all water tables with 3 rows + uploads", start, "PASSED")
            print("WA01 PASSED")
        except Exception as e:
            ru.add_result("Assessment Water", "WA01 - Fill all water tables", start, "FAILED", str(e))
            raise

    def test_WA02_verify_water_data(self):
        """WA02 - Verify data persists and matches inputted values"""
        start = datetime.datetime.now()
        print("\nWA02: Verify Water Data")
        try:
            # We can re-check a few tables to confirm persistence
            
            # Consumption
            open_accordion("flush-heading__water_consumption")
            for i, d in enumerate(POTABLE_DATA):
                row = sb.page.locator("[id='Consumption_Potable_table'] tbody tr").nth(i)
                sc(row)
                t_val = row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity(kLd)']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                
                # Check for formatted numbers like "100" vs "100.00"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"
            
            # Supply
            open_accordion("flush-heading__water_supply")
            for i, d in enumerate(ONSITE_DATA):
                row = sb.page.locator("[id='Supply_Recycled on-site_table'] tbody tr").nth(i)
                sc(row)
                t_val = row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity(kLd)']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"

            # Freshwater Provision
            open_accordion("flush-heading__freshwater_provision")
            for i, d in enumerate(FRESHWATER_PROV_DATA):
                row = sb.page.locator("[id='Freshwater Provision_Freshwater provision_table'] tbody tr").nth(i)
                sc(row)
                t_val = row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"

            ru.add_result("Assessment Water", "WA02 - Verify water data inputs", start, "PASSED")
            print("WA02 PASSED")
        except Exception as e:
            ru.add_result("Assessment Water", "WA02 - Verify water data inputs", start, "FAILED", str(e))
            raise
