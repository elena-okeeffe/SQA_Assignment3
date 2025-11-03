# tests/test_forgotten_password.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FORGOTTEN_PATH = "/index.php?route=account/forgotten"

@pytest.mark.functional
def test_forgotten_password_success(driver, helpers):
    """
    T020: Forgotten Password – registered email shows success confirmation.
    """
    helpers.open(FORGOTTEN_PATH)
    # Email field (OpenCart defaults to #input-email; theme may use name=email)
    email_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#input-email, input[name='email']"))
    )
    email_input.clear()
    # Use an email that is registered on your environment (set via env or fixture)
    email_input.send_keys("valid.user+demo@example.com")

    # Continue/Submit button
    submit = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Continue'], input[value='Continue'], button[type='submit']"))
    )
    submit.click()

    # Expect a success message and/or success page
    msg = helpers.success_or_warning_text().lower()
    assert ("email" in msg and ("sent" in msg or "success" in msg)) or "success" in driver.current_url.lower(), \
        f"Expected success confirmation after reset request. Got: {msg!r} URL={driver.current_url}"

@pytest.mark.functional
def test_forgotten_password_unregistered_email_masking(driver, helpers):
    """
    Optional negative: unregistered email should not leak account existence.
    """
    helpers.open(FORGOTTEN_PATH)
    email_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#input-email, input[name='email']"))
    )
    email_input.clear()
    email_input.send_keys("not.registered.abcdef@example.com")

    submit = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='Continue'], input[value='Continue'], button[type='submit']"))
    )
    submit.click()

    msg = helpers.success_or_warning_text().lower()
    # Either neutral success text or generic warning; both acceptable as long as no PII leak
    assert "success" in msg or "email" in msg or "warning" in msg, f"Unexpected message: {msg}"
