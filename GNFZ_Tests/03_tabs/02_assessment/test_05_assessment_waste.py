import sys, os, time
import datetime
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import report_utils as ru
import shared_browser as sb

NZE_WASTE_BTN = "#net-zero-waste-assessment"
PAUSE = 1000

# --- DATA ---
GENERATED_DATA = [
    {"type": "Concrete", "qty": "1000"},
    {"type": "Wood",     "qty": "500"},
    {"type": "Glass",    "qty": "200"},
]
LANDFILL_DATA = [
    {"type": "Asbestos", "qty": "50"},
    {"type": "Metal: mixed cans", "qty": "10"},
    {"type": "Household residual waste", "qty": "300"},
]
INCINERATED_DATA = [
    {"type": "Mineral Oil", "qty": "20"},
    {"type": "Wood", "qty": "100"},
    {"type": "Paper and board: mixed", "qty": "50"},
]
COMPOSTED_DATA = [
    {"type": "Organic: food and drink waste", "qty": "200"},
    {"type": "Organic: garden waste", "qty": "100"},
    {"type": "Wood", "qty": "50"},
]
RECYCLED_DATA = [
    {"type": "Metals", "qty": "300"},
    {"type": "Glass", "qty": "100"},
    {"type": "Paper and board: paper", "qty": "400"},
]
REUSED_DATA = [
    {"type": "Bricks", "qty": "200"},
    {"type": "Wood", "qty": "100"},
    {"type": "Plastics: average plastics", "qty": "50"},
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

    upload_icon = row.locator("i.bi-paperclip, img[src*='upload'], i[title*='upload'], i[class*='paperclip']").first
    if upload_icon.count() > 0:
        sc(upload_icon)
        try:
            upload_icon.click(timeout=3000)
        except:
            upload_icon.evaluate("el => el.click()")
        
        sb.page.wait_for_timeout(2000) # wait for modal to fully open
        
        modal = sb.page.locator(".modal-content").filter(has_text="File upload").first
        if modal.count() == 0:
            modal = sb.page.locator(".modal-content").last

        if modal.count() > 0 and modal.is_visible():
            add_files = modal.locator("#gnfz-files-add-more, a:has-text('Add files'), button:has-text('Add Files'), button:has-text('Choose files'), button:has-text('Browse')").first
            if add_files.count() == 0:
                add_files = sb.page.locator("#gnfz-files-add-more, a:has-text('Add files'), button:has-text('Add Files')").first

            # Try method 1: Intercept file chooser by clicking the "Add files" button
            upload_done = False
            if add_files.count() > 0 and add_files.is_visible():
                try:
                    with sb.page.expect_file_chooser(timeout=5000) as fc_info:
                        add_files.click(timeout=3000)
                    file_chooser = fc_info.value
                    file_chooser.set_files(file_paths)
                    print(f"        ✅ Uploaded {num_files} files via file chooser")
                    upload_done = True
                except Exception as chooser_err:
                    print(f"        ⚠️ File chooser click failed: {chooser_err}. Trying input direct upload...")

            # Try method 2: Direct upload using input[type='file'] if method 1 failed or wasn't applicable
            if not upload_done:
                file_input = modal.locator("input[type='file'], input#file-uploader-scope").first
                if file_input.count() == 0:
                    file_input = sb.page.locator("input[type='file']").first
                
                if file_input.count() > 0:
                    try:
                        file_input.set_input_files(file_paths, timeout=5000)
                        print(f"        ✅ Uploaded {num_files} files directly")
                        upload_done = True
                    except Exception as direct_err:
                        print(f"        ❌ Direct upload failed: {direct_err}")
                else:
                    print("        ⚠️ File input not found")
                    
            if upload_done and num_files > 1:
                view_more = modal.locator("text='View more', .view-more-btn").first
                if view_more.count() > 0 and view_more.is_visible():
                    try:
                        view_more.click(timeout=3000)
                    except:
                        view_more.evaluate("el => el.click()")
                    sb.page.wait_for_timeout(1000)
                    print("        ✅ Clicked View more")
                    
                showing = modal.locator("span.text-secondary", has_text="Showing").first
                if showing.count() > 0:
                    print(f"        ✅ Found text: {showing.inner_text()}")
                else:
                    print("        ⚠️ Showing X of X files text not found")

            # Click Upload/Save confirmation inside modal if present
            confirm_btn = modal.locator("button:has-text('Upload'), button:has-text('Save'), .modal-footer button.native-button").first
            if confirm_btn.count() > 0 and confirm_btn.is_visible():
                try:
                    confirm_btn.click(timeout=3000)
                    sb.page.wait_for_timeout(1000)
                except Exception:
                    pass

            close_btn = modal.locator("#modal-generic-close, .btn-close, .modal-header .close").first
            if close_btn.count() == 0:
                close_btn = sb.page.locator("#modal-generic-close, .btn-close, .modal-header .close").first
                
            if close_btn.count() > 0 and close_btn.is_visible():
                try:
                    close_btn.click(timeout=3000)
                except:
                    close_btn.evaluate("el => el.click()")
                sb.page.wait_for_timeout(500)
            else:
                sb.page.keyboard.press("Escape")
                sb.page.wait_for_timeout(500)



def click_save():
    save_btn = sb.page.locator("button:has-text('Save'):visible, #gnfz-save:visible, .btn:has-text('Save'):visible").first
    sc(save_btn)
    sb.page.wait_for_timeout(500)
    save_btn.click(force=True, timeout=10000)
    sb.page.wait_for_timeout(2500)

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
    f_inps = tfoot.locator("input")
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
            inps = row.locator("input[readonly]")
            inp = inps.last if inps.count() > 0 else row.locator("input:not([type='search']):not([list])").last
                
        if inp.count() > 0:
            val = inp.input_value().replace(',', '').strip()
            try: calc_sum += float(val)
            except: pass
            
    diff = abs(footer_total - calc_sum)
    assert diff < 2.0, f"{table_sel} Total Mismatch: Footer {footer_total} vs Calc {calc_sum}"
    print(f"    ✅ Total Verified: {footer_total:,.2f}")


class TestAssessmentWasteTab:

    @classmethod
    def setup_class(cls):
        print("\n\nWaste Tab: Clicking Net Zero Waste tab...")
        sb.page.locator(NZE_WASTE_BTN).first.click()
        sb.page.wait_for_timeout(PAUSE)
        sb.page.wait_for_selector("#net-zero-waste", timeout=15_000)
        print("Waste tab ready.\n")

    @classmethod
    def teardown_class(cls):
        # We can close the browser now or save the final report.
        # But maybe we leave it open just in case another file runs.
        print("\nAssessment Waste done. Browser stays open.\n")

    def test_WS01_fill_all_waste_tables(self):
        """WS01 - Fill all Waste tables (Generated, Landfill, Incinerated, Composted, Recycled, Reused)"""
        start = datetime.datetime.now()
        print("\nWS01: Fill all Waste tables")
        try:
            # a. Generated
            open_accordion("header_0")
            log_t("1a. Generated")
            ensure_rows("[id='Generated_table']", 3)
            for i, d in enumerate(GENERATED_DATA):
                row = sb.page.locator("[id='Generated_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste generated", d["qty"])
                n_files = 15 if i == 0 else 1
                upload_file_for_row(row, num_files=n_files)

            # b. Sent to Landfill
            open_accordion("header_1")
            log_t("1b. Sent to Landfill")
            ensure_rows("[id='Sent to Landfill_table']", 3)
            for i, d in enumerate(LANDFILL_DATA):
                row = sb.page.locator("[id='Sent to Landfill_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste sent to landfill", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Sent to Landfill_table']")

            # c. Incinerated
            open_accordion("header_2")
            log_t("1c. Incinerated")
            ensure_rows("[id='Incinerated_table']", 3)
            for i, d in enumerate(INCINERATED_DATA):
                row = sb.page.locator("[id='Incinerated_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste Incinerated", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Incinerated_table']")

            # d. Composted
            open_accordion("header_3")
            log_t("1d. Composted")
            ensure_rows("[id='Composted_table']", 3)
            for i, d in enumerate(COMPOSTED_DATA):
                row = sb.page.locator("[id='Composted_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste Composted", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Composted_table']")

            # e. Recycled
            open_accordion("header_4")
            log_t("1e. Recycled")
            ensure_rows("[id='Recycled_table']", 3)
            for i, d in enumerate(RECYCLED_DATA):
                row = sb.page.locator("[id='Recycled_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste recycled", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Recycled_table']")

            # f. Reused
            open_accordion("header_5")
            log_t("1f. Reused")
            ensure_rows("[id='Reused_table']", 3)
            for i, d in enumerate(REUSED_DATA):
                row = sb.page.locator("[id='Reused_table'] tbody tr").nth(i)
                sc(row)
                fill_search(row, d["type"])
                fill_by_addrs(row, "Quantity of Waste Reused", d["qty"])
                upload_file_for_row(row)

            verify_table_total("[id='Reused_table']")

            # Save the entire form
            print("  Clicking Save to persist inputs...")
            click_save()

            ru.add_result("Assessment Waste", "WS01 - Fill all waste tables with 3 rows + uploads", start, "PASSED")
            print("WS01 PASSED")
        except Exception as e:
            ru.add_result("Assessment Waste", "WS01 - Fill all waste tables", start, "FAILED", str(e))
            raise

    def test_WS02_verify_waste_data(self):
        """WS02 - Verify data persists and matches inputted values"""
        start = datetime.datetime.now()
        print("\nWS02: Verify Waste Data")
        try:
            
            # Generated
            open_accordion("header_0")
            for i, d in enumerate(GENERATED_DATA):
                row = sb.page.locator("[id='Generated_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"
            
            # Sent to Landfill
            open_accordion("header_1")
            for i, d in enumerate(LANDFILL_DATA):
                row = sb.page.locator("[id='Sent to Landfill_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"

            # Incinerated
            open_accordion("header_2")
            for i, d in enumerate(INCINERATED_DATA):
                row = sb.page.locator("[id='Incinerated_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"
                
            # Composted
            open_accordion("header_3")
            for i, d in enumerate(COMPOSTED_DATA):
                row = sb.page.locator("[id='Composted_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"
                
            # Recycled
            open_accordion("header_4")
            for i, d in enumerate(RECYCLED_DATA):
                row = sb.page.locator("[id='Recycled_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"
                
            # Reused
            open_accordion("header_5")
            for i, d in enumerate(REUSED_DATA):
                row = sb.page.locator("[id='Reused_table'] tbody tr").nth(i)
                sc(row)
                t_ng = row.locator(".ng-value-label").first
                t_val = t_ng.inner_text().strip() if t_ng.count() > 0 and t_ng.is_visible() else row.locator("input[type='search'], input[list]").first.input_value()
                q_val = row.locator("input[assessment_addrs*='Quantity']").first.input_value()
                assert d["type"] == t_val, f"Mismatch Type: {d['type']} vs {t_val}"
                expected_q = float(d["qty"])
                actual_q = float(q_val.replace(',', ''))
                assert expected_q == actual_q, f"Mismatch Qty: {d['qty']} vs {q_val}"

            ru.add_result("Assessment Waste", "WS02 - Verify waste data inputs after save", start, "PASSED")
            print("WS02 PASSED")
        except Exception as e:
            ru.add_result("Assessment Waste", "WS02 - Verify waste data inputs after save", start, "FAILED", str(e))
            raise
