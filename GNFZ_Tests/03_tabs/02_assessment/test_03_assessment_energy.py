import sys, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import datetime
import report_utils as ru
import shared_browser as sb

NZE_ENERGY_BTN = "#net-zero-energy-assessment"
PAUSE = 1000

FUELS_DATA = [
    {"fuel": "Natural gas",                  "consumption": "1000"},
    {"fuel": "Diesel (100% mineral diesel)", "consumption": "500"},
    {"fuel": "LPG",                          "consumption": "250"},
]
MOBILE_DATA = [
    {"fuel": "Diesel (100% mineral diesel)", "consumption": "300"},
    {"fuel": "Gasoline",                     "consumption": "200"},
    {"fuel": "CNG",                          "consumption": "100"},
]
ENERGY_DATA = [
    {"activity": "Non Renewable Electricity from Grid\u200b", "consumption": "5000"},
    {"activity": "Solar Energy",                              "consumption": "2000"},
    {"activity": "Wind Energy",                               "consumption": "1500"},
]

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
                    print(f"        ⚠️ Direct file chooser failed: {chooser_err}. Trying input direct upload...")

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
                view_more = modal.locator(":text('View more'), .view-more-btn").first
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

class TestAssessmentEnergyTab:

    @classmethod
    def setup_class(cls):
        print("\n\nEnergy Tab: Clicking Net Zero Energy tab...")
        sb.page.locator(NZE_ENERGY_BTN).first.click()
        sb.page.wait_for_timeout(PAUSE)
        sb.page.wait_for_selector("#net-zero-energy", timeout=15_000)
        print("Energy tab ready.\n")

    @classmethod
    def teardown_class(cls):
        print("\nAssessment Energy done. Browser stays open.\n")

    def test_EN01_verify_scope1_data(self):
        """EN01 - Scope 1 patched values from Emissions"""
        start = datetime.datetime.now()
        print("\nEN01: Verify Scope 1 patched data")
        try:
            open_accordion("energy-heading__Scope1")
            
            # Fuels
            print("  Checking 1a. Fuels...")
            for i, d in enumerate(FUELS_DATA):
                row = sb.page.locator("[id='scope1_Fuels_table'] tbody tr").nth(i)
                sc(row)
                fuel_val = row.locator("input[type='search'], input[list]").first.input_value()
                cons_val = row.locator("input[assessment_addrs*='Consumption']").first.input_value()
                
                cons_expected = float(d["consumption"])
                cons_actual = float(cons_val.replace(',', ''))
                
                assert d["fuel"] == fuel_val, f"Row {i} Fuel mismatch: expected '{d['fuel']}', got '{fuel_val}'"
                assert cons_expected == cons_actual, f"Row {i} Consumption mismatch: expected '{d['consumption']}', got '{cons_val}'"
                upload_file_for_row(row)
                print(f"    ✅ Row {i+1}: {d['fuel']} - {d['consumption']}")

            # Mobile Combustion
            print("  Checking 1b. Mobile Combustion...")
            for i, d in enumerate(MOBILE_DATA):
                row = sb.page.locator("[id='scope1_Mobile Combustion_table'] tbody tr").nth(i)
                sc(row)
                fuel_val = row.locator("input[type='search'], input[list]").first.input_value()
                cons_val = row.locator("input[assessment_addrs*='Consumption']").first.input_value()
                
                cons_expected = float(d["consumption"])
                cons_actual = float(cons_val.replace(',', ''))
                
                assert d["fuel"] == fuel_val, f"Row {i} Fuel mismatch: expected '{d['fuel']}', got '{fuel_val}'"
                assert cons_expected == cons_actual, f"Row {i} Consumption mismatch: expected '{d['consumption']}', got '{cons_val}'"
                upload_file_for_row(row)
                print(f"    ✅ Row {i+1}: {d['fuel']} - {d['consumption']}")

            ru.add_result("Assessment Energy", "EN01 - Scope 1 patched values", start, "PASSED")
            print("EN01 PASSED")
        except Exception as e:
            ru.add_result("Assessment Energy", "EN01 - Scope 1 patched values", start, "FAILED", str(e))
            raise

    def test_EN02_verify_scope2_data(self):
        """EN02 - Scope 2 patched values from Emissions"""
        start = datetime.datetime.now()
        print("\nEN02: Verify Scope 2 patched data")
        try:
            open_accordion("energy-heading__Scope2")
            
            # Energy
            print("  Checking 2c. Energy...")
            for i, d in enumerate(ENERGY_DATA):
                row = sb.page.locator("[id='scope2_Energy_table'] tbody tr").nth(i)
                sc(row)
                act_val = row.locator("input[type='search'], input[list]").first.input_value()
                cons_val = row.locator("input[assessment_addrs*='Consumption']").first.input_value()
                
                cons_expected = float(d["consumption"])
                cons_actual = float(cons_val.replace(',', ''))
                
                assert d["activity"] == act_val, f"Row {i} Activity mismatch: expected '{d['activity']}', got '{act_val}'"
                assert cons_expected == cons_actual, f"Row {i} Consumption mismatch: expected '{d['consumption']}', got '{cons_val}'"
                upload_file_for_row(row)
                print(f"    ✅ Row {i+1}: {d['activity']} - {d['consumption']}")

            ru.add_result("Assessment Energy", "EN02 - Scope 2 patched values", start, "PASSED")
            print("EN02 PASSED")
        except Exception as e:
            ru.add_result("Assessment Energy", "EN02 - Scope 2 patched values", start, "FAILED", str(e))
            raise
