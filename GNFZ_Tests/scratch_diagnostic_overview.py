import os
import sys
import time
from playwright.sync_api import sync_playwright

def run():
    print("Starting Playwright diagnostics...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        # 1. Login
        print("Navigating to login page...")
        page.goto("https://dev-platform.globalnetworkforzero.com/login", wait_until="domcontentloaded")
        page.wait_for_selector("#gnfz-login-email", timeout=15000)
        
        page.fill("#gnfz-login-email", "aishwarya@promantus.com")
        page.fill("#gnfz-login-password", "Aishu@1234")
        page.click("button.myform-btn")
        
        print("Waiting for login redirect...")
        page.wait_for_url(lambda url: "login" not in url, timeout=20000)
        print(f"Logged in successfully. Current URL: {page.url}")
        
        # 2. Go to list and find a project
        if "project/list" in page.url:
            print("On project list. Clicking first project...")
            project_link = page.locator("a[href*='/project/building/'], td a").first
            if project_link.count() > 0:
                project_link.click()
                page.wait_for_timeout(3000)
            else:
                page.goto("https://dev-platform.globalnetworkforzero.com/project/building", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
        
        print(f"Project page URL: {page.url}")
        
        # Go to Overview tab
        print("Clicking Overview Tab...")
        overview_tab = page.locator("label[for='tab1'], li#gnfz-overview label, li#gnfz-overview").first
        overview_tab.click()
        page.wait_for_timeout(2000)
        
        # Find complete assessment dropdown
        complete_select = page.locator("select#gnfz-complete-assessment, select[id*='complete-assessment']").first
        print(f"Complete Assessment dropdown visible: {complete_select.is_visible()}")
        
        # Select "Submit for review"
        complete_select.select_option(label="Submit for review")
        page.wait_for_timeout(1000)
        
        # Click YES on confirmation
        yes_btn = page.locator("button#simple-process-status-submit-change-event-popup, button:has-text('YES')").first
        if yes_btn.count() > 0 and yes_btn.is_visible():
            print("Clicking YES confirmation popup...")
            yes_btn.click()
            page.wait_for_timeout(2000)
        
        # Let's inspect the entire DOM of the page to find error messages, popups, or alerts
        print("\n--- Searching for active alerts, dialogs, toasts, or errors ---")
        
        # 1. Take a screenshot
        os.makedirs("test_output/screenshots", exist_ok=True)
        screenshot_path = "test_output/screenshots/diagnostic_overview.png"
        page.screenshot(path=screenshot_path)
        print(f"Saved diagnostic screenshot to {screenshot_path}")
        
        # 2. Check Swal (SweetAlert2) elements
        swal_elements = page.locator(".swal2-container, .swal2-popup, .swal2-title, .swal2-html-container")
        print(f"Swal elements count: {swal_elements.count()}")
        for i in range(swal_elements.count()):
            print(f"Swal Element {i}: Class = {swal_elements.nth(i).get_attribute('class')} | Text = {swal_elements.nth(i).inner_text().strip()}")
            print(f"HTML: {swal_elements.nth(i).evaluate('el => el.outerHTML')[:500]}")
            
        # 3. Check text-danger, alert-danger, invalid-feedback, toast, etc.
        other_errs = page.locator(".text-danger, .invalid-feedback, .alert-danger, .toast, .toast-body, #error-message, small")
        print(f"Other potential error elements count: {other_errs.count()}")
        for i in range(other_errs.count()):
            el = other_errs.nth(i)
            if el.is_visible():
                print(f"Visible Element {i}: Tag = {el.evaluate('el => el.tagName')} | Class = {el.get_attribute('class')} | Text = {el.inner_text().strip()}")
                
        # 4. Print body html search for keywords like 'Please submit', 'assessment', 'certification'
        body_text = page.locator("body").inner_text()
        print("\n--- Does body text contain 'Please submit'? ---")
        print("Please submit" in body_text)
        print("\n--- Does body text contain 'certification'? ---")
        print("certification" in body_text)
        
        browser.close()

if __name__ == "__main__":
    run()
