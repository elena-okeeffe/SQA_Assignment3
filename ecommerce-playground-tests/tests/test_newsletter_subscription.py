# tests/test_newsletter_subscription.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NEWSLETTER_PATH = "/index.php?route=account/newsletter"

def _radio(driver, value_str):
    # OpenCart uses name='newsletter' values '1' (Yes) and '0' (No)
    return driver.find_element(By.CSS_SELECTOR, f"input[name='newsletter'][value='{value_str}']")

@pytest.mark.functional
def test_newsletter_subscribe_and_unsubscribe(driver, helpers, creds):
    """
    T022: Newsletter – toggle Yes/No and verify persistence.
    """
    helpers.login(creds["email"], creds["password"])

    # --- Subscribe (Yes) ---
    helpers.open(NEWSLETTER_PATH)
    yes = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='newsletter'][value='1']"))
    )
    yes.click()

    # Continue button (often an input[type=submit] or button)
    cont = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], input[value='Continue']"))
    )
    cont.click()

    # Expect confirmation
    msg = helpers.success_or_warning_text().lower()
    assert "success" in msg or "updated" in msg or "modified" in msg, f"Expected success after subscribing. Got: {msg!r}"

    # Re-open page and verify radio state persisted
    helpers.open(NEWSLETTER_PATH)
    yes_checked = driver.find_element(By.CSS_SELECTOR, "input[name='newsletter'][value='1']").is_selected()
    assert yes_checked, "Newsletter 'Yes' should persist after subscribe"

    # --- Unsubscribe (No) ---
    no = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='newsletter'][value='0']"))
    )
    no.click()
    cont = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], input[value='Continue']"))
    )
    cont.click()

    msg2 = helpers.success_or_warning_text().lower()
    assert "success" in msg2 or "updated" in msg2 or "modified" in msg2, f"Expected success after unsubscribing. Got: {msg2!r}"

    # Re-open and verify persisted
    helpers.open(NEWSLETTER_PATH)
    no_checked = driver.find_element(By.CSS_SELECTOR, "input[name='newsletter'][value='0']").is_selected()
    assert no_checked, "Newsletter 'No' should persist after unsubscribe"
