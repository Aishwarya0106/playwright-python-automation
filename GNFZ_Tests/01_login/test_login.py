import datetime
import pytest
from playwright.sync_api import sync_playwright, expect
import report_utils as ru
import shared_browser as sb

BASE_URL = "https://dev-platform.globalnetworkforzero.com/login"

REG_FIRST_NAME    = "Test"
REG_LAST_NAME     = "User"
REG_EMAIL         = "testuser_gnfz@mailinator.com"
REG_PASSWORD      = "Test@1234"
REG_WRONG_CONFIRM = "Test@9999"

SIGN_UP_LINK      = "a.active-a-link:has-text('Sign up')"
SIGN_IN_LINK      = "a.active-a-link:has-text('Sign in')"
FIRST_NAME_INPUT  = "#gnfz-register-firstName"
LAST_NAME_INPUT   = "#gnfz-register-lastName"
SU_EMAIL_INPUT    = "#gnfz-register-email"
SU_PASSWORD_INPUT = "#gnfz-register-password"
CONFIRM_PWD_INPUT = "#gnfz-register-confirmPassword"
SIGN_UP_BUTTON    = "#gnfz-sign-up-button"

FORGOT_PASSWORD_LINK  = "a.font-weight-500:has-text('Forgot password')"
FP_EMAIL_INPUT        = "#gnfz-forget-email"
RESET_PASSWORD_BUTTON = "#reset-password"
FP_EMAIL_REQUIRED_MSG = "small.text-danger:has-text('Email is required')"
FP_EMAIL_INVALID_MSG  = "small.text-danger:has-text('Email is invalid')"
CHECK_EMAIL_MSG       = "p:has-text('Check your email')"
FP_SIGN_IN_LINK       = "#gnfz-remember-password a:has-text('Sign in')"

SI_EMAIL_INPUT           = "#gnfz-login-email"
SI_PASSWORD_INPUT        = "#gnfz-login-password"
SI_SIGN_IN_BUTTON        = "button.myform-btn"
SI_EMAIL_REQUIRED_MSG    = "small.text-danger:has-text('Email is required')"
SI_PASSWORD_REQUIRED_MSG = "small.text-danger:has-text('Password is required')"
SI_INVALID_LOGIN_MSG     = "small.text-danger:has-text('Invalid login or password')"

VALID_EMAIL    = "aishwarya@promantus.com"
VALID_PASSWORD = "Aishu@1234"
WRONG_PASSWORD = "WrongPass@999"
INVALID_EMAIL  = "aishwarya.com"

PAUSE = 1000


def get_visible_errors(page):
    result = []
    els = page.locator("small.text-danger")
    for i in range(els.count()):
        el = els.nth(i)
        if el.is_visible():
            txt = el.inner_text().strip()
            if txt:
                result.append(txt)
    return result


def fill_field(page, selector, value):
    page.click(selector)
    page.wait_for_timeout(300)
    page.fill(selector, value)
    page.wait_for_timeout(300)


def clear_signup_fields(page):
    page.wait_for_timeout(600)
    for sel in [FIRST_NAME_INPUT, LAST_NAME_INPUT,
                SU_EMAIL_INPUT, SU_PASSWORD_INPUT, CONFIRM_PWD_INPUT]:
        try:
            page.fill(sel, "")
        except Exception:
            pass
    page.wait_for_timeout(400)


def clear_signin_fields(page):
    try:
        page.wait_for_timeout(800)
        page.fill(SI_EMAIL_INPUT, "")
        page.wait_for_timeout(300)
        page.fill(SI_PASSWORD_INPUT, "")
        page.wait_for_timeout(400)
    except Exception:
        pass


class TestSignUp:

    @classmethod
    def setup_class(cls):
        ru.start_timer()
        if getattr(sb, "pw", None) is None:
            sb.pw = sync_playwright().start()
        if getattr(sb, "browser", None) is None:
            sb.browser = sb.pw.chromium.launch(headless=False, slow_mo=800, args=["--start-maximized"])
        if getattr(sb, "context", None) is None:
            sb.context = sb.browser.new_context(no_viewport=True)
        if getattr(sb, "page", None) is None:
            sb.page = sb.context.new_page()
        print(f"\n\nStep 1: Navigating to {BASE_URL}")
        sb.page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
        sb.page.wait_for_selector(SIGN_UP_LINK, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Step 2: Clicking Sign up link")
        sb.page.click(SIGN_UP_LINK)
        sb.page.wait_for_selector(SIGN_UP_BUTTON, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Sign Up page ready\n")

    @classmethod
    def teardown_class(cls):
        print("\nStep 4: Clicking Sign in link")
        sb.page.wait_for_selector(SIGN_IN_LINK, timeout=10_000)
        sb.page.click(SIGN_IN_LINK)
        sb.page.wait_for_selector(SI_SIGN_IN_BUTTON, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Step 5: Sign In page ready\n")

    def setup_method(self, method):
        if sb.page.locator(SIGN_UP_BUTTON).count() == 0:
            sb.page.click(SIGN_UP_LINK)
            sb.page.wait_for_selector(SIGN_UP_BUTTON, timeout=10_000)
            sb.page.wait_for_timeout(PAUSE)

    def teardown_method(self, method):
        clear_signup_fields(sb.page)
        try:
            if sb.page.locator(SIGN_UP_BUTTON).count() == 0:
                sb.page.click(SIGN_UP_LINK)
                sb.page.wait_for_selector(SIGN_UP_BUTTON, timeout=10_000)
                sb.page.wait_for_timeout(PAUSE)
        except Exception:
            pass

    def test_SU01_signup_without_any_data(self):
        start = datetime.datetime.now()
        print("\nSU01: Sign Up without any data")
        try:
            sb.page.click(SIGN_UP_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            errors = get_visible_errors(sb.page)
            assert len(errors) > 0
            ru.add_result("Sign Up", "SU01 - Signup without any data", start, "PASSED")
            print(f"SU01 PASSED - {errors}")
        except Exception as e:
            ru.add_result("Sign Up", "SU01 - Signup without any data", start, "FAILED", str(e))
            raise

    def test_SU02_signup_with_first_name_only(self):
        start = datetime.datetime.now()
        print("\nSU02: First Name only")
        try:
            fill_field(sb.page, FIRST_NAME_INPUT, REG_FIRST_NAME)
            sb.page.click(SIGN_UP_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            errors = get_visible_errors(sb.page)
            assert len(errors) > 0
            ru.add_result("Sign Up", "SU02 - Signup with first name only", start, "PASSED")
            print(f"SU02 PASSED - {errors}")
        except Exception as e:
            ru.add_result("Sign Up", "SU02 - Signup with first name only", start, "FAILED", str(e))
            raise

    def test_SU03_signup_with_first_last_email_only(self):
        start = datetime.datetime.now()
        print("\nSU03: First Name, Last Name, Email only")
        try:
            fill_field(sb.page, FIRST_NAME_INPUT, REG_FIRST_NAME)
            fill_field(sb.page, LAST_NAME_INPUT,  REG_LAST_NAME)
            fill_field(sb.page, SU_EMAIL_INPUT,   REG_EMAIL)
            sb.page.click(SIGN_UP_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            errors = get_visible_errors(sb.page)
            assert len(errors) > 0
            ru.add_result("Sign Up", "SU03 - Signup first, last, email only", start, "PASSED")
            print(f"SU03 PASSED - {errors}")
        except Exception as e:
            ru.add_result("Sign Up", "SU03 - Signup first, last, email only", start, "FAILED", str(e))
            raise

    def test_SU04_signup_password_mismatch(self):
        start = datetime.datetime.now()
        print("\nSU04: Mismatched passwords")
        try:
            fill_field(sb.page, FIRST_NAME_INPUT,  REG_FIRST_NAME)
            fill_field(sb.page, LAST_NAME_INPUT,   REG_LAST_NAME)
            fill_field(sb.page, SU_EMAIL_INPUT,    REG_EMAIL)
            fill_field(sb.page, SU_PASSWORD_INPUT, REG_PASSWORD)
            fill_field(sb.page, CONFIRM_PWD_INPUT, REG_WRONG_CONFIRM)
            sb.page.click(SIGN_UP_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            errors = get_visible_errors(sb.page)
            assert len(errors) > 0
            ru.add_result("Sign Up", "SU04 - Signup password mismatch", start, "PASSED")
            print(f"SU04 PASSED - {errors}")
        except Exception as e:
            ru.add_result("Sign Up", "SU04 - Signup password mismatch", start, "FAILED", str(e))
            raise


class TestForgotPassword:

    @classmethod
    def setup_class(cls):
        print("\nStep 6: Clicking Forgot password link")
        sb.page.wait_for_selector(FORGOT_PASSWORD_LINK, timeout=10_000)
        sb.page.click(FORGOT_PASSWORD_LINK)
        sb.page.wait_for_selector(RESET_PASSWORD_BUTTON, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Forgot Password page ready\n")

    @classmethod
    def teardown_class(cls):
        print("\nStep 7: Clicking Sign in link")
        sb.page.wait_for_selector(FP_SIGN_IN_LINK, timeout=10_000)
        sb.page.click(FP_SIGN_IN_LINK)
        sb.page.wait_for_selector(SI_SIGN_IN_BUTTON, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)
        print("Step 8: Sign In page ready\n")

    def teardown_method(self, method):
        try:
            sb.page.wait_for_timeout(800)
            if sb.page.locator(FP_EMAIL_INPUT).count() > 0:
                sb.page.fill(FP_EMAIL_INPUT, "")
                sb.page.wait_for_timeout(400)
        except Exception:
            pass

    def test_FP01_reset_without_email(self):
        start = datetime.datetime.now()
        print("\nFP01: Reset without email")
        try:
            sb.page.click(RESET_PASSWORD_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(FP_EMAIL_REQUIRED_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Forgot Password", "FP01 - Reset without email", start, "PASSED")
            print("FP01 PASSED")
        except Exception as e:
            ru.add_result("Forgot Password", "FP01 - Reset without email", start, "FAILED", str(e))
            raise

    def test_FP02_reset_with_invalid_email(self):
        start = datetime.datetime.now()
        print("\nFP02: Reset with invalid email")
        try:
            fill_field(sb.page, FP_EMAIL_INPUT, INVALID_EMAIL)
            sb.page.click(RESET_PASSWORD_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(FP_EMAIL_INVALID_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Forgot Password", "FP02 - Reset with invalid email", start, "PASSED")
            print("FP02 PASSED")
        except Exception as e:
            ru.add_result("Forgot Password", "FP02 - Reset with invalid email", start, "FAILED", str(e))
            raise

    def test_FP03_reset_with_valid_email(self):
        start = datetime.datetime.now()
        print(f"\nFP03: Reset with valid email {VALID_EMAIL}")
        try:
            fill_field(sb.page, FP_EMAIL_INPUT, VALID_EMAIL)
            sb.page.click(RESET_PASSWORD_BUTTON)
            sb.page.wait_for_timeout(PAUSE * 2)
            expect(sb.page.locator(CHECK_EMAIL_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Forgot Password", "FP03 - Reset with valid email", start, "PASSED")
            print("FP03 PASSED")
        except Exception as e:
            ru.add_result("Forgot Password", "FP03 - Reset with valid email", start, "FAILED", str(e))
            raise


class TestSignIn:

    @classmethod
    def setup_class(cls):
        print("\nStep 9: Sign In page active\n")
        sb.page.wait_for_selector(SI_SIGN_IN_BUTTON, timeout=30_000)
        sb.page.wait_for_timeout(PAUSE)

    @classmethod
    def teardown_class(cls):
        print("\nSign In tests done. Browser stays open for Create New Project.\n")

    def teardown_method(self, method):
        clear_signin_fields(sb.page)

    def test_TC01_login_without_email_and_password(self):
        start = datetime.datetime.now()
        print("\nTC01: No credentials")
        try:
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(SI_EMAIL_REQUIRED_MSG)).to_be_visible()
            expect(sb.page.locator(SI_PASSWORD_REQUIRED_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC01 - Login without email and password", start, "PASSED")
            print("TC01 PASSED")
        except Exception as e:
            ru.add_result("Sign In", "TC01 - Login without email and password", start, "FAILED", str(e))
            raise

    def test_TC02_login_without_email_with_password(self):
        start = datetime.datetime.now()
        print("\nTC02: Password only")
        try:
            fill_field(sb.page, SI_PASSWORD_INPUT, VALID_PASSWORD)
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(SI_EMAIL_REQUIRED_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC02 - Login without email with password", start, "PASSED")
            print("TC02 PASSED")
        except Exception as e:
            ru.add_result("Sign In", "TC02 - Login without email with password", start, "FAILED", str(e))
            raise

    def test_TC03_login_with_email_without_password(self):
        start = datetime.datetime.now()
        print("\nTC03: Email only")
        try:
            fill_field(sb.page, SI_EMAIL_INPUT, VALID_EMAIL)
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(SI_PASSWORD_REQUIRED_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC03 - Login with email without password", start, "PASSED")
            print("TC03 PASSED")
        except Exception as e:
            ru.add_result("Sign In", "TC03 - Login with email without password", start, "FAILED", str(e))
            raise

    def test_TC04_login_with_valid_email_wrong_password(self):
        start = datetime.datetime.now()
        print("\nTC04: Wrong password")
        try:
            fill_field(sb.page, SI_EMAIL_INPUT,    VALID_EMAIL)
            fill_field(sb.page, SI_PASSWORD_INPUT, WRONG_PASSWORD)
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator(SI_INVALID_LOGIN_MSG)).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC04 - Login with wrong password", start, "PASSED")
            print("TC04 PASSED")
        except Exception as e:
            ru.add_result("Sign In", "TC04 - Login with wrong password", start, "FAILED", str(e))
            raise

    def test_TC05_login_with_invalid_email_format(self):
        start = datetime.datetime.now()
        print("\nTC05: Invalid email format")
        try:
            fill_field(sb.page, SI_EMAIL_INPUT,    INVALID_EMAIL)
            fill_field(sb.page, SI_PASSWORD_INPUT, VALID_PASSWORD)
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            expect(sb.page.locator("small.text-danger").first).to_be_visible()
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC05 - Login with invalid email format", start, "PASSED")
            print("TC05 PASSED")
        except Exception as e:
            ru.add_result("Sign In", "TC05 - Login with invalid email format", start, "FAILED", str(e))
            raise

    def test_TC06_login_with_valid_credentials(self):
        start = datetime.datetime.now()
        print("\nTC06: Valid credentials")
        try:
            fill_field(sb.page, SI_EMAIL_INPUT,    VALID_EMAIL)
            fill_field(sb.page, SI_PASSWORD_INPUT, VALID_PASSWORD)
            sb.page.click(SI_SIGN_IN_BUTTON)
            sb.page.wait_for_timeout(PAUSE)
            sb.page.wait_for_url(lambda url: "login" not in url, timeout=20_000)
            sb.page.wait_for_timeout(PAUSE)
            ru.add_result("Sign In", "TC06 - Login with valid credentials", start, "PASSED")
            print(f"TC06 PASSED - Redirected to {sb.page.url}")
        except Exception as e:
            ru.add_result("Sign In", "TC06 - Login with valid credentials", start, "FAILED", str(e))
            pytest.fail(str(e))