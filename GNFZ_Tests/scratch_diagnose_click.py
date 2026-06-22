import os
import sys
from playwright.sync_api import sync_playwright

def run():
    print("Starting Playwright...")
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
        
        # 2. Go to project/list
        page.goto("https://dev-platform.globalnetworkforzero.com/project/list", wait_until="networkidle")
        page.wait_for_selector("table tbody tr, tr", timeout=15000)
        
        print("\n--- Printing Table Rows ---")
        rows = page.locator("table tbody tr, tr")
        print(f"Total rows found: {rows.count()}")
        for i in range(min(rows.count(), 10)):
            txt = rows.nth(i).inner_text().strip().replace('\n', ' | ')
            print(f"Row {i}: {txt}")
            # print(rows.nth(i).evaluate("el => el.outerHTML")[:500])
            
        browser.close()

if __name__ == "__main__":
    run()
