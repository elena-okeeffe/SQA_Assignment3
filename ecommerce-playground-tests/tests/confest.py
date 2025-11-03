# conftest.py
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://ecommerce-playground.lambdatest.io"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def creds():
    # 👉 Put a valid registered test account here
    return {
        "email": os.environ.get("ECOM_EMAIL", "valid.user+demo@example.com"),
        "password": os.environ.get("ECOM_PASSWORD", "Password123!")
    }

@pytest.fixture
def driver():
    chrome_opts = Options()
    # Headless for CI; comment out if you want to see the browser
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1400,1000")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_opts)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()

def wait_visible(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )

def wait_clickable(driver, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )

@pytest.fixture
def helpers(driver, base_url):
    class H:
        def open(self, path):
            driver.get(f"{base_url}{path}")

        def login(self, email, password):
            self.open("/index.php?route=account/login")
            # Email + password
            wait_visible(driver, (By.CSS_SELECTOR, "#input-email, input[name='email']")).send_keys(email)
            wait_visible(driver, (By.CSS_SELECTOR, "#input-password, input[name='password']")).send_keys(password)
            # Submit
            submit = wait_clickable(driver, (By.CSS_SELECTOR, "input[type='submit'][value='Login'], input[value='Login'], button[type='submit']"))
            submit.click()
            # Assert some account element is present (My Account breadcrumb)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".breadcrumb, #content"))
            )

        def success_or_warning_text(self):
            # Collect common alert classes on this theme
            alerts = driver.find_elements(By.CSS_SELECTOR, ".alert, .alert-success, .alert-danger, .alert-warning, .alert-dismissible")
            if alerts:
                return " ".join(a.text.strip() for a in alerts if a.text.strip())
            # Fallback: content area message
            content = driver.find_elements(By.CSS_SELECTOR, "#content")
            return content[0].text.strip() if content else ""

        def goto_pdp(self, product_id=107):
            # Default to iPhone PDP (product_id=107 on LT demo)
            self.open(f"/index.php?route=product/product&product_id={product_id}")
            wait_visible(driver, (By.CSS_SELECTOR, "#content"))

    return H()
