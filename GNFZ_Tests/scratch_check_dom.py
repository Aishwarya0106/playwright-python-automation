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
        
        # 2. Go to a project page if not on one
        if "project/list" in page.url:
            print("On project list. Clicking first project...")
            # Let's try to click a project link or navigate directly
            project_link = page.locator("a[href*='/project/building/'], td a").first
            if project_link.count() > 0:
                project_link.click()
                page.wait_for_timeout(3000)
            else:
                # Fallback: Navigate to the create page
                page.goto("https://dev-platform.globalnetworkforzero.com/project/building", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
        
        print(f"Project page URL: {page.url}")
        
        # 3. Print the outerHTML of all elements matching the tab selectors
        page.wait_for_selector(".pc-tab nav ul, li label", timeout=15000)
        
        print("\n--- HTML of Tab list container (.pc-tab nav ul) ---")
        tab_container = page.locator(".pc-tab nav ul, nav ul").first
        if tab_container.count() > 0:
            print(tab_container.inner_html())
        else:
            print("Tab container not found.")
            
        print("\n--- OuterHTML of individual Tab items ---")
        tab_items = page.locator(".pc-tab nav ul li, nav ul li, label[for^='tab']")
        for i in range(tab_items.count()):
            print(f"Item {i}:")
            print(tab_items.nth(i).evaluate("el => el.outerHTML"))
            print("-" * 40)
            
        browser.close()

if __name__ == "__main__":
    run()
