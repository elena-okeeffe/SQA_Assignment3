# pages/register_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
import re


class RegisterPage(BasePage):
    FIRST_NAME = (By.ID, "input-firstname")
    LAST_NAME = (By.ID, "input-lastname")
    EMAIL = (By.ID, "input-email")
    TELEPHONE = (By.ID, "input-telephone")
    PASSWORD = (By.ID, "input-password")
    CONFIRM = (By.ID, "input-confirm")
    PRIVACY_LABEL = (By.CSS_SELECTOR, "label[for='input-agree']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "input[value='Continue']")
    ALERT_DANGER = (By.CSS_SELECTOR, ".alert.alert-danger.alert-dismissible")

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)

    def open_from_home(self):
        # assumes BasePage.visit("") opens the home page
        self.visit("")
        try:
            # find register via header; prefer waiting for clickable element
            register_locator = (By.XPATH, "//span[normalize-space()='Register']")
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(register_locator))
            register_btn = self.driver.find_element(*register_locator)
            try:
                register_btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", register_btn)
        except Exception:
            # fallback: navigate directly to register page
            self.visit("index.php?route=account/register")
        self.wait_for_page_ready()

    def fill_registration_form(self, first, last, email, telephone, password):
        self.wait.until(EC.element_to_be_clickable(self.FIRST_NAME))
        el = self.find(*self.FIRST_NAME); el.clear(); el.send_keys(first)
        el = self.find(*self.LAST_NAME); el.clear(); el.send_keys(last)
        el = self.find(*self.EMAIL); el.clear(); el.send_keys(email)
        el = self.find(*self.TELEPHONE); el.clear(); el.send_keys(telephone)
        el = self.find(*self.PASSWORD); el.clear(); el.send_keys(password)
        el = self.find(*self.CONFIRM); el.clear(); el.send_keys(password)

    def agree_privacy(self):
        lbl = self.find(*self.PRIVACY_LABEL)
        try:
            lbl.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", lbl)

    def submit(self):
        btn = self.find(*self.CONTINUE_BUTTON)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def get_alert_text(self, timeout=5):
        """
        Wait for the danger alert to be visible, then return a cleaned message.
        If the alert contains an icon or extra whitespace, return the first
        "Warning: ..." match if found, otherwise the stripped text.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.visibility_of_element_located(self.ALERT_DANGER))
            raw = el.text.strip()

            # Prefer an explicit "Warning: ..." substring if present
            m = re.search(r"(Warning:\s*.+)", raw, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()

            # Fallback: remove leading non-word characters (icons) and return the rest
            cleaned = re.sub(r"^[^\w]+", "", raw).strip()
            return cleaned
        except Exception:
            return ""