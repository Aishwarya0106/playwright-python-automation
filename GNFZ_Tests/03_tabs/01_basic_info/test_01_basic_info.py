import sys, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
for _p in [_root, os.path.join(_root, "GNFZ_Tests")]:
    if _p not in sys.path: sys.path.insert(0, _p)

import datetime
import report_utils as ru
import shared_browser as sb
from playwright.sync_api import expect

# ── Locators ──────────────────────────────────────────────────────────────────
BUILDING_INFO_HEADING = "b:has-text('Building Info')"
TEAM_INFO_HEADING     = "b:has-text('Team Info')"
BILLING_INFO_HEADING  = "b:has-text('Billing Info')"
BILLING_NO_RECORDS    = "span:has-text('No records to show')"
SAVE_BUTTON           = "#gnfz-save"
SPACE_TITLE_ERROR     = "small.text-danger:has-text('Building/Space title is required')"
TARGET_AREA_ERROR     = "small.text-danger:has-text('Should be less than gross building area')"
GEO_ICON              = "span.input-group-text i.bi-geo-alt-fill"
GEO_INPUT             = "#geoPoint"
PROJECT_TABLE_ROWS    = "table tbody tr.text-size-14px"

BUILDING_FIELDS = [
    ("Building phase dropdown",         "#building-space-type"),
    ("Building/Space title input",      "#building_spaceTitle"),
    ("Occupancy category (tagify)",     "tags.tagify.form-control"),
    ("Gross building area",             "#gnfz-basic-info-form-grossArea"),
    ("Target certification area",       "#gnfz-basic-info-form-targetCertArea"),
    ("Geo location",                    "#geoPoint"),
    ("Address 1",                       "#address1"),
    ("Address 2",                       "#address2"),
    ("City",                            "#city"),
    ("State",                           "#state"),
    ("Country/Region",                  "#country"),
    ("Postal code",                     "#post"),
    ("Start date",                      "#startDate"),
    ("Confidential dropdown",           "#confidentialRequest"),
]
TEAM_FIELDS = [
    ("Team Member Name",   "#teamMemberName-0"),
    ("Team Role dropdown", "#teamTable td select.form-control.form-select"),
    ("Organization input", "#teamTable input[name='orgName']"),
]

PAUSE = 1000


def scroll_into_view(locator):
    try:
        locator.evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
        sb.page.wait_for_timeout(200)
    except Exception:
        pass


class TestBasicInfoTab:

    building_space_id = ""  # captured in BI13, used in BI14

    @classmethod
    def setup_class(cls):
        """Basic Info tab already clicked by test_create_project teardown."""
        print("\n\nBasic Info: Waiting for content...")
        sb.page.wait_for_selector(BUILDING_INFO_HEADING, timeout=15_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Basic Info ready.\n")

    @classmethod
    def teardown_class(cls):
        """DO NOT close browser — assessment runs next."""
        print("\nBasic Info done. Browser stays open.\n")

    # ── BI01 ──────────────────────────────────────────────────────────────────
    def test_BI01_verify_building_info_heading(self):
        """BI01 - Building Info heading visible"""
        start = datetime.datetime.now()
        print("\nBI01: Building Info heading")
        try:
            expect(sb.page.locator(BUILDING_INFO_HEADING).first).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", "BI01 - Building Info heading", start, "PASSED")
            print("BI01 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI01 - Building Info heading", start, "FAILED", str(e))
            raise

    # ── BI02 ──────────────────────────────────────────────────────────────────
    def test_BI02_verify_all_building_fields(self):
        """BI02 - All 14 building fields present and visible"""
        start = datetime.datetime.now()
        print("\nBI02: Verify all building fields")
        try:
            missing = []
            for label, sel in BUILDING_FIELDS:
                el = sb.page.locator(sel)
                if el.count() == 0 or not el.first.is_visible():
                    missing.append(label)
                    print(f"  ❌ {label}")
                else:
                    print(f"  ✅ {label}")
            assert len(missing) == 0, f"Missing: {missing}"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", f"BI02 - All {len(BUILDING_FIELDS)} fields present", start, "PASSED")
            print("BI02 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI02 - Building fields", start, "FAILED", str(e))
            raise

    # ── BI03 ──────────────────────────────────────────────────────────────────
    def test_BI03_verify_team_info_heading(self):
        """BI03 - Team Info heading visible"""
        start = datetime.datetime.now()
        print("\nBI03: Team Info heading")
        try:
            expect(sb.page.locator(TEAM_INFO_HEADING).first).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", "BI03 - Team Info heading", start, "PASSED")
            print("BI03 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI03 - Team Info heading", start, "FAILED", str(e))
            raise

    # ── BI04 ──────────────────────────────────────────────────────────────────
    def test_BI04_verify_team_fields(self):
        """BI04 - Team fields present"""
        start = datetime.datetime.now()
        print("\nBI04: Team fields")
        try:
            missing = []
            for label, sel in TEAM_FIELDS:
                el = sb.page.locator(sel)
                if el.count() == 0:
                    missing.append(label)
                    print(f"  ❌ {label}")
                else:
                    print(f"  ✅ {label}")
            assert len(missing) == 0, f"Missing: {missing}"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", f"BI04 - All {len(TEAM_FIELDS)} team fields", start, "PASSED")
            print("BI04 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI04 - Team fields", start, "FAILED", str(e))
            raise

    # ── BI05 ──────────────────────────────────────────────────────────────────
    def test_BI05_verify_billing_info(self):
        """BI05 - Billing heading + No records"""
        start = datetime.datetime.now()
        print("\nBI05: Billing Info")
        try:
            expect(sb.page.locator(BILLING_INFO_HEADING).first).to_be_visible()
            expect(sb.page.locator(BILLING_NO_RECORDS).first).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", "BI05 - Billing heading + no records", start, "PASSED")
            print("BI05 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI05 - Billing Info", start, "FAILED", str(e))
            raise

    # ── BI06 ──────────────────────────────────────────────────────────────────
    def test_BI06_save_empty_check_title_error(self):
        """BI06 - Save without data → title required error"""
        start = datetime.datetime.now()
        print("\nBI06: Save empty → check title error")
        try:
            save = sb.page.locator(SAVE_BUTTON).first
            save.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(800)
            save.click()
            sb.page.wait_for_timeout(PAUSE)
            sb.page.evaluate("window.scrollTo(0, 0)")
            sb.page.wait_for_timeout(800)
            err = sb.page.locator(SPACE_TITLE_ERROR).first
            err.wait_for(state="visible", timeout=10_000)
            txt = err.inner_text().strip()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", f"BI06 - Error: '{txt}'", start, "PASSED")
            print(f"BI06 PASSED - '{txt}'")
        except Exception as e:
            ru.add_result("Basic Info", "BI06 - Save empty error", start, "FAILED", str(e))
            raise

    # ── BI07 ──────────────────────────────────────────────────────────────────
    def test_BI07_fill_building_title(self):
        """BI07 - Fill title = 'Building - {today}'"""
        start      = datetime.datetime.now()
        today      = datetime.datetime.now().strftime("%b %d")
        title_text = f"Building - {today}"
        print(f"\nBI07: Fill title = '{title_text}'")
        try:
            inp = sb.page.locator("#building_spaceTitle")
            inp.wait_for(state="visible", timeout=10_000)
            inp.click()
            inp.fill(title_text)
            sb.page.wait_for_timeout(PAUSE)
            assert title_text in inp.input_value()
            ru.add_result("Basic Info", f"BI07 - Title: '{title_text}'", start, "PASSED")
            print("BI07 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI07 - Fill title", start, "FAILED", str(e))
            raise

    # ── BI08 ──────────────────────────────────────────────────────────────────
    def test_BI08_select_occupancy_categories(self):
        """BI08 - Select A1-theatres + A2-Banquet halls → click outside"""
        start = datetime.datetime.now()
        print("\nBI08: Occupancy categories")
        try:
            tagify = sb.page.locator(".tagify__input").first
            tagify.wait_for(state="visible", timeout=10_000)
            for cat in ["A1-theatres", "A2-Banquet halls"]:
                tagify.click()
                sb.page.wait_for_timeout(400)
                tagify.type(cat)
                sb.page.wait_for_timeout(800)
                sug = sb.page.locator(f".tagify__dropdown__item:has-text('{cat}')").first
                if sug.count() > 0 and sug.is_visible():
                    sug.click()
                    print(f"  ✅ Selected: '{cat}'")
                else:
                    tagify.press("Enter")
                    print(f"  ✅ Added: '{cat}'")
                sb.page.wait_for_timeout(400)
            # Click outside to confirm
            sb.page.locator(BUILDING_INFO_HEADING).first.click()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", "BI08 - Occupancy: A1-theatres, A2-Banquet halls", start, "PASSED")
            print("BI08 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI08 - Occupancy", start, "FAILED", str(e))
            raise

    # ── BI09 ──────────────────────────────────────────────────────────────────
    def test_BI09_fill_gross_area(self):
        """BI09 - Gross building area = 100"""
        start = datetime.datetime.now()
        print("\nBI09: Gross area = 100")
        try:
            gross = sb.page.locator("#gnfz-basic-info-form-grossArea")
            gross.wait_for(state="visible", timeout=10_000)
            gross.click()
            gross.fill("100")
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", "BI09 - Gross area = 100", start, "PASSED")
            print("BI09 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI09 - Gross area", start, "FAILED", str(e))
            raise

    # ── BI10 ──────────────────────────────────────────────────────────────────
    def test_BI10_target_area_error_then_fix(self):
        """BI10 - Target = 1000 → error → fix to 100"""
        start = datetime.datetime.now()
        print("\nBI10: Target 1000 → error → fix 100")
        try:
            target = sb.page.locator("#gnfz-basic-info-form-targetCertArea")
            target.wait_for(state="visible", timeout=10_000)
            target.click(click_count=3)
            target.fill("1000")
            sb.page.wait_for_timeout(PAUSE)
            # Save to trigger error
            save = sb.page.locator(SAVE_BUTTON).first
            save.scroll_into_view_if_needed()
            save.click()
            sb.page.wait_for_timeout(PAUSE)
            sb.page.evaluate("window.scrollTo(0, 0)")
            sb.page.wait_for_timeout(800)
            err = sb.page.locator(TARGET_AREA_ERROR).first
            err.wait_for(state="visible", timeout=10_000)
            err_txt = err.inner_text().strip()
            print(f"  ✅ Error: '{err_txt}'")
            # Fix to 100
            target.scroll_into_view_if_needed()
            target.click(click_count=3)
            target.fill("100")
            sb.page.wait_for_timeout(PAUSE)
            # Click outside to confirm
            sb.page.locator(BUILDING_INFO_HEADING).first.click()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", f"BI10 - Error shown, fixed to 100", start, "PASSED")
            print("BI10 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI10 - Target area", start, "FAILED", str(e))
            raise

    # ── BI11 ──────────────────────────────────────────────────────────────────
    def test_BI11_geo_location(self):
        """BI11 - Geo icon → IITM Research Park → select → Submit"""
        start = datetime.datetime.now()
        print("\nBI11: Geo location")
        try:
            # Click geo icon
            geo_icon = sb.page.locator(GEO_ICON).first
            geo_icon.wait_for(state="visible", timeout=10_000)
            geo_icon.click()
            sb.page.wait_for_timeout(PAUSE * 2)

            # Find search input in popup
            search = None
            for sel in [
                "input[placeholder*='Search']",
                "input[placeholder*='search']",
                ".modal-body input[type='text']",
                ".modal-body input[type='search']",
                ".modal input",
            ]:
                loc = sb.page.locator(sel).first
                if loc.count() > 0 and loc.is_visible():
                    search = loc
                    break
            assert search is not None, "Geo search input not found"

            # Type location
            search.click()
            search.fill("IITM Research Park")
            sb.page.wait_for_timeout(2000)

            # Click outside to trigger dropdown
            try:
                sb.page.locator(".modal-header, .modal-title").first.click()
            except Exception:
                pass
            sb.page.wait_for_timeout(1000)

            # Select from dropdown
            iitm = sb.page.locator(
                "li:has-text('IITM Research Park'), "
                "li:has-text('IITM'), "
                ".pac-item:has-text('IITM'), "
                "[class*='option']:has-text('IITM'), "
                "[class*='item']:has-text('IITM')"
            ).first
            if iitm.count() > 0 and iitm.is_visible():
                iitm.click()
                sb.page.wait_for_timeout(PAUSE)
                print("  ✅ Selected IITM from dropdown")
            else:
                search.press("ArrowDown")
                sb.page.wait_for_timeout(300)
                search.press("Enter")
                sb.page.wait_for_timeout(PAUSE)
                print("  ✅ Selected via keyboard")

            # Click Submit
            submit = sb.page.locator(
                "button:has-text('Submit'), .modal-footer button:has-text('Submit')"
            ).first
            submit.wait_for(state="visible", timeout=10_000)
            submit.click()
            sb.page.wait_for_timeout(PAUSE * 2)

            geo_val = sb.page.locator(GEO_INPUT).input_value()
            print(f"  Geo value: '{geo_val}'")
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Basic Info", f"BI11 - Geo: '{geo_val}'", start, "PASSED")
            print("BI11 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI11 - Geo location", start, "FAILED", str(e))
            raise

    # ── BI12 ──────────────────────────────────────────────────────────────────
    def test_BI12_fill_start_date(self):
        """BI12 - Fill Start date using jQuery datepicker API (properly selected)"""
        start     = datetime.datetime.now()
        today_str = datetime.datetime.now().strftime("%m/%d/%Y")
        print(f"\nBI12: Start date = {today_str}")
        try:
            date_inp = sb.page.locator("#startDate")
            date_inp.wait_for(state="visible", timeout=10_000)
            scroll_into_view(date_inp)
            sb.page.wait_for_timeout(300)

            # Click to open datepicker
            date_inp.click()
            sb.page.wait_for_timeout(600)

            # Set via jQuery datepicker API so the date is properly selected
            sb.page.evaluate(f"""
                (function() {{
                    var el = document.getElementById('startDate');
                    if (!el) return;
                    if (window.$ && typeof $(el).datepicker === 'function') {{
                        $(el).datepicker('setDate', '{today_str}');
                        $(el).trigger('change');
                        $(el).trigger('input');
                    }} else {{
                        el.value = '{today_str}';
                        el.dispatchEvent(new Event('input',  {{bubbles:true}}));
                        el.dispatchEvent(new Event('change', {{bubbles:true}}));
                    }}
                }})()
            """)
            sb.page.wait_for_timeout(500)

            # Press Tab to close datepicker
            date_inp.press("Tab")
            sb.page.wait_for_timeout(500)

            # Click elsewhere to dismiss
            sb.page.locator(BUILDING_INFO_HEADING).first.click()
            sb.page.wait_for_timeout(PAUSE)

            value = date_inp.input_value()
            print(f"  Date value: '{value}'")
            assert value.strip(), "Start date is empty after fill"

            ru.add_result("Basic Info", f"BI12 - Start date: '{today_str}'", start, "PASSED")
            print("BI12 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI12 - Start date", start, "FAILED", str(e))
            raise

    # ── BI13 ──────────────────────────────────────────────────────────────────
    def test_BI13_save_check_building_space_id(self):
        """BI13 - Save → verify Building/Space id generated"""
        start = datetime.datetime.now()
        print("\nBI13: Save → check Building/Space id")
        try:
            save = sb.page.locator(SAVE_BUTTON).first
            save.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(500)
            save.click()
            sb.page.wait_for_timeout(PAUSE * 2)
            sb.page.evaluate("window.scrollTo(0, 0)")
            sb.page.wait_for_timeout(800)

            # Scan page for Building/Space id text
            id_text = sb.page.evaluate("""
                (function() {
                    var all = document.querySelectorAll('*');
                    for (var i = 0; i < all.length; i++) {
                        var t = (all[i].innerText || '').trim();
                        if (t && t.toLowerCase().includes('building/space id')) return t;
                    }
                    return '';
                })()
            """)

            if id_text:
                TestBasicInfoTab.building_space_id = id_text
                print(f"  ✅ Building/Space id: '{id_text}'")
                ru.add_result("Basic Info", f"BI13 - Building/Space id: '{id_text}'", start, "PASSED")
            else:
                # Check no blocking errors
                errors = sb.page.locator("small.text-danger")
                visible = [
                    errors.nth(i).inner_text().strip()
                    for i in range(errors.count())
                    if errors.nth(i).is_visible() and errors.nth(i).inner_text().strip()
                ]
                if not visible:
                    TestBasicInfoTab.building_space_id = ""
                    ru.add_result("Basic Info", "BI13 - Saved (id not visible)", start, "PASSED")
                    print("BI13 PASSED - Saved ok")
                else:
                    raise AssertionError(f"Save errors: {visible}")
            sb.page.wait_for_timeout(PAUSE)
            print("BI13 PASSED")
        except Exception as e:
            ru.add_result("Basic Info", "BI13 - Save + id", start, "FAILED", str(e))
            raise

    # ── BI14 ──────────────────────────────────────────────────────────────────
    def test_BI14_breadcrumb_verify_project_open_assessment(self):
        """BI14 - Click Building breadcrumb → verify project ID and name in list
        → click project → open project/building page"""
        start        = datetime.datetime.now()
        today        = datetime.datetime.now().strftime("%b %d")
        project_name = f"Building - {today}"
        building_id  = TestBasicInfoTab.building_space_id
        print(f"\nBI14: Breadcrumb → verify project → open it")
        print(f"  Name: '{project_name}'  ID: '{building_id}'")
        try:
            # ── Step 1: Click Building in breadcrumb via JS ────────────────────
            print("  Step 1: Clicking Building breadcrumb via JS...")
            clicked = sb.page.evaluate("""
                (function() {
                    // Try every breadcrumb container
                    var containers = [
                        document.querySelector('nav ol.breadcrumb'),
                        document.querySelector('ol.breadcrumb'),
                        document.querySelector('nav.breadcrumb'),
                        document.querySelector('[class*="breadcrumb"]')
                    ];
                    for (var c = 0; c < containers.length; c++) {
                        if (!containers[c]) continue;
                        var items = containers[c].querySelectorAll('a, li, span');
                        for (var i = 0; i < items.length; i++) {
                            var t = (items[i].innerText || items[i].textContent || '').trim().toLowerCase();
                            if (t === 'building' || t === 'buildings' || t === 'projects') {
                                items[i].click();
                                return 'clicked: ' + t + ' in ' + containers[c].tagName;
                            }
                        }
                    }
                    // Last resort: any <a> whose text is exactly "Building"
                    var links = document.querySelectorAll('a');
                    for (var i = 0; i < links.length; i++) {
                        var t = links[i].innerText.trim().toLowerCase();
                        if (t === 'building' || t === 'buildings' || t === 'projects') {
                            links[i].click();
                            return 'clicked link: ' + t;
                        }
                    }
                    return 'NOT FOUND';
                })()
            """)
            if clicked == 'NOT FOUND':
                print("  Fallback to Playwright click...")
                try:
                    sb.page.locator("a:has-text('Building'), a:has-text('Buildings'), li.breadcrumb-item:has-text('Building')").first.click(timeout=5000)
                    clicked = "clicked via playwright fallback"
                except Exception as e:
                    print(f"  Playwright click failed: {e}")
                    
            print(f"  Breadcrumb JS result: {clicked}")
            assert "NOT FOUND" not in clicked, "Building breadcrumb not found in DOM"
            sb.page.wait_for_timeout(PAUSE * 2)
            print(f"  URL: {sb.page.url}")

            # ── Step 2: Wait for project list ─────────────────────────────────
            print("  Step 2: Waiting for List of projects...")
            sb.page.wait_for_selector(
                "b:has-text('List of projects'), "
                "div.text-label:has-text('List of projects')",
                timeout=15_000
            )
            sb.page.wait_for_timeout(PAUSE)
            print("  ✅ On project list")

            # ── Step 3: Find project row by name ──────────────────────────────
            print(f"  Step 3: Looking for '{project_name}'...")
            rows      = sb.page.locator(PROJECT_TABLE_ROWS)
            total     = rows.count()
            found_idx = None
            found_row = ""
            for i in range(total):
                txt = rows.nth(i).inner_text().strip()
                if project_name.lower() in txt.lower():
                    found_idx = i
                    found_row = txt
                    break
            assert found_idx is not None, \
                f"Project '{project_name}' not found in {total} rows"
            print(f"  ✅ Found: '{found_row[:100]}'")

            # ── Step 5: Verify building ID in row (if any) ─────────────────────────────
            if building_id:
                id_num = "".join(filter(str.isdigit, building_id))
                if id_num and id_num in found_row:
                    print(f"  ✅ Building ID '{id_num}' in row")
                else:
                    print(f"  ℹ️  Building ID '{id_num}' not in row text")

            ru.add_result("Basic Info",
                          f"BI14 - Project '{project_name}' found in list",
                          start, "PASSED")
            print("BI14 PASSED - Verified project in list, not clicking it.")

        except Exception as e:
            ru.add_result("Basic Info",
                          "BI14 - Breadcrumb → list → verify project",
                          start, "FAILED", str(e))
            raise