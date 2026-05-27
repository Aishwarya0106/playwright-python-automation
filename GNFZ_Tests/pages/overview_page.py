import shared_browser as sb
from pages import ui_utils as uu

class OverviewPage:
    def __init__(self):
        self.page = sb.page
        
        # Locators
        self.overview_tab = self.page.locator("li#gnfz-overview")
        
        # Selectors inside overview
        self.building_info_select = self.page.locator("select#gnfz-building-info")
        self.team_info_select = self.page.locator("select#gnfz-team-info")
        self.complete_assessment_select = self.page.locator("select#gnfz-complete-assessment")
        self.net_zero_plans_select = self.page.locator("select#gnfz-nzp")
        self.error_message = self.page.locator(".text-danger.text-left.text-size-14px").first

    def navigate_to_overview(self):
        uu.wait_for_page_stable(self.page)
        uu.safe_click(self.page, self.overview_tab, wait_after=2000)

    def are_all_fields_visible(self):
        return (
            self.building_info_select.is_visible() and
            self.team_info_select.is_visible() and
            self.complete_assessment_select.is_visible() and
            self.net_zero_plans_select.is_visible()
        )

    def submit_assessment_for_review(self):
        uu.sc(self.complete_assessment_select)
        self.complete_assessment_select.select_option(label="Submit for review")
        self.page.wait_for_timeout(500)

    def get_error_message(self):
        if self.error_message.is_visible():
            return self.error_message.inner_text().strip()
        return ""
