import datetime
import pytest
from playwright.sync_api import expect
import report_utils as ru
import shared_browser as sb

# ── URLs ──────────────────────────────────────────────────────────────────────
PROJECT_LIST_URL     = "project/list"
PROJECT_BUILDING_URL = "project/building"

# ── Locators ──────────────────────────────────────────────────────────────────
CREATE_PROJECT_BUTTON = "#gnfz-create-project"
CATEGORY_CARDS        = "#project-categories h4.card-title"
TAB_LABELS            = ".pc-tab nav ul li label"
BREADCRUMB_ITEMS      = "nav ol.breadcrumb li"
NET_ZERO_HEADING      = "h3"
BASIC_INFO_TAB        = "#gnfz-basicInfo label"
BUILDING_INFO_HEADING = "b:has-text('Building Info')"

PAUSE = 1000


class TestCreateNewProject:

    @classmethod
    def setup_class(cls):
        """
        After TC06 login → lands on project/list
        → Always click Create new project button
        → Select Building card → navigate to project/building
        """
        print("\n\nStep 11: Checking page after login...")
        sb.page.wait_for_timeout(PAUSE)
        current_url = sb.page.url
        print(f"  Current URL: {current_url}")

        # ── Already on project/building — nothing to do ───────────────────────
        if PROJECT_BUILDING_URL in current_url:
            print("  Already on project/building. Continuing...")
            return

        # ── Must be on project/list — click Create new project ────────────────
        if PROJECT_LIST_URL in current_url:
            print("  On project/list. Clicking Create new project button...")
            btn = sb.page.locator(CREATE_PROJECT_BUTTON)
            btn.wait_for(state="visible", timeout=15_000)
            sb.page.wait_for_timeout(500)
            btn.scroll_into_view_if_needed()
            sb.page.wait_for_timeout(300)
            btn.click()
            sb.page.wait_for_timeout(PAUSE * 2)
            print(f"  Navigated to: {sb.page.url}")
        else:
            print(f"  Unexpected URL: {current_url}")
            raise AssertionError(f"Expected project/list URL but got: {current_url}")

        # ── Find Building card dynamically and click ──────────────────────────
        print("  Waiting for category cards...")
        sb.page.wait_for_selector(CATEGORY_CARDS, timeout=15_000)
        sb.page.wait_for_timeout(500)

        all_cards      = sb.page.locator(CATEGORY_CARDS)
        total          = all_cards.count()
        building_index = None

        for i in range(total):
            name = all_cards.nth(i).inner_text().strip()
            if name.lower() == "building":
                building_index = i
                break

        if building_index is None:
            raise AssertionError("Building card not found on project/menu page")

        print(f"  Found Building at position {building_index + 1} of {total}. Clicking...")
        building_card = all_cards.nth(building_index)
        building_card.scroll_into_view_if_needed()
        sb.page.wait_for_timeout(300)
        building_card.click()
        sb.page.wait_for_timeout(PAUSE * 2)
        print(f"  Navigated to: {sb.page.url}\n")

    @classmethod
    def teardown_class(cls):
        """CNP tests done. Click Basic Info tab so test_02_basic_info.py continues."""
        print("\nCNP tests done. Clicking Basic Info tab for next test file...")
        try:
            tab = sb.page.locator(BASIC_INFO_TAB)
            tab.wait_for(state="visible", timeout=10_000)
            sb.page.wait_for_timeout(300)
            tab.click()
            sb.page.wait_for_timeout(PAUSE)
            sb.page.wait_for_selector(BUILDING_INFO_HEADING, timeout=15_000)
            sb.page.wait_for_timeout(PAUSE)
            print("Basic Info tab clicked and content loaded.\n")
        except Exception as e:
            print(f"Could not click Basic Info tab: {e}")

    def test_CNP01_verify_building_page_loaded(self):
        """CNP01 - Verify URL is project/building"""
        start = datetime.datetime.now()
        print("\nCNP01: Verify building page URL")
        try:
            current_url = sb.page.url
            assert PROJECT_BUILDING_URL in current_url, \
                f"Expected '{PROJECT_BUILDING_URL}' but got: {current_url}"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Create New Project", f"CNP01 - Building page loaded: {current_url}", start, "PASSED")
            print(f"CNP01 PASSED - {current_url}")
        except Exception as e:
            ru.add_result("Create New Project", "CNP01 - Building page loaded", start, "FAILED", str(e))
            raise

    def test_CNP02_verify_breadcrumb(self):
        """CNP02 - Dynamically verify breadcrumb contains Building"""
        start = datetime.datetime.now()
        print("\nCNP02: Verify breadcrumb")
        try:
            sb.page.wait_for_selector(BREADCRUMB_ITEMS, timeout=15_000)
            crumbs     = sb.page.locator(BREADCRUMB_ITEMS)
            crumb_list = [crumbs.nth(i).inner_text().strip()
                          for i in range(crumbs.count())
                          if crumbs.nth(i).inner_text().strip()]
            print(f"  Breadcrumb: {crumb_list}")
            assert len(crumb_list) >= 2, f"Expected at least 2 items: {crumb_list}"
            assert "building" in " ".join(crumb_list).lower(), \
                f"'Building' not in breadcrumb: {crumb_list}"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Create New Project", f"CNP02 - Breadcrumb: {' > '.join(crumb_list)}", start, "PASSED")
            print(f"CNP02 PASSED - {' > '.join(crumb_list)}")
        except Exception as e:
            ru.add_result("Create New Project", "CNP02 - Breadcrumb verified", start, "FAILED", str(e))
            raise

    def test_CNP03_verify_net_zero_certification_heading(self):
        """CNP03 - Verify Net Zero certification heading is visible"""
        start = datetime.datetime.now()
        print("\nCNP03: Verify Net Zero certification heading")
        try:
            all_h3     = sb.page.locator(NET_ZERO_HEADING)
            found_text = None
            for i in range(all_h3.count()):
                h3 = all_h3.nth(i)
                if h3.is_visible():
                    text = h3.inner_text().strip()
                    if "net zero" in text.lower():
                        found_text = text
                        break
            assert found_text is not None, "Net Zero certification heading not found"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Create New Project", f"CNP03 - Heading: '{found_text}'", start, "PASSED")
            print(f"CNP03 PASSED - '{found_text}'")
        except Exception as e:
            ru.add_result("Create New Project", "CNP03 - Net Zero heading visible", start, "FAILED", str(e))
            raise

    def test_CNP04_verify_all_tabs_dynamically(self):
        """CNP04 - Dynamically read all tab labels and verify each is visible"""
        start = datetime.datetime.now()
        print("\nCNP04: Reading all tabs dynamically...")
        try:
            sb.page.wait_for_selector(TAB_LABELS, timeout=15_000)
            sb.page.wait_for_timeout(500)
            all_tabs    = sb.page.locator(TAB_LABELS)
            total       = all_tabs.count()
            assert total > 0, "No tab labels found"
            tabs_found  = []
            not_visible = []
            for i in range(total):
                tab  = all_tabs.nth(i)
                name = tab.inner_text().strip()
                if name:
                    tabs_found.append(name)
                    if not tab.is_visible():
                        not_visible.append(name)
            assert len(not_visible) == 0, f"Tabs not visible: {not_visible}"
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Create New Project", f"CNP04 - All {len(tabs_found)} tabs visible: {tabs_found}", start, "PASSED")
            print(f"CNP04 PASSED - {len(tabs_found)} tabs: {tabs_found}")
        except Exception as e:
            ru.add_result("Create New Project", "CNP04 - All tabs visible", start, "FAILED", str(e))
            raise