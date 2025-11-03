# tests/test_review_submission.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PDP_PATH = "/index.php?route=product/product&product_id=107"  # iPhone

@pytest.mark.functional
def test_review_submission_logged_in(driver, helpers, creds):
    """
    T021: Product Review – logged-in user submits a valid review.
    """
    helpers.login(creds["email"], creds["password"])
    helpers.open(PDP_PATH)

    # Open the Reviews tab (many OpenCart themes have #tab-review or an anchor with text)
    # Try a few robust locators:
    for css in ["a[href='#tab-review']", "a[data-toggle='tab'][href*='review']", "li a[href*='review']"]:
        tabs = driver.find_elements(By.CSS_SELECTOR, css)
        if tabs:
            tabs[0].click()
            break

    # Wait for review form presence (try multiple selectors)
    name_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "#input-name, input[name='name'], input#name"
        ))
    )
    review_textarea = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "#input-review, textarea[name='text'], textarea#review"
        ))
    )

    name_input.clear()
    name_input.send_keys("Sizhe")

    # ≥ 25–30 chars to avoid 'text length' validation
    review_textarea.clear()
    review_textarea.send_keys("Good build quality and stable performance in daily use.")

    # Rating radios (OpenCart: input[name='rating'][value='4'] etc.)
    rating = driver.find_elements(By.CSS_SELECTOR, "input[name='rating'][value='4'], input[name='rating'][value='5']")
    assert rating, "Rating radio input not found"
    rating[0].click()

    # Submit review (OpenCart classic: #button-review or input[value='Continue'])
    submit = None
    for css in ["#button-review", "button#button-review", "input[value='Continue']", "button[type='submit']"]:
        elems = driver.find_elements(By.CSS_SELECTOR, css)
        if elems:
            submit = elems[0]
            break
    assert submit, "Review submit button not found"
    submit.click()

    msg = helpers.success_or_warning_text().lower()
    assert "thank you" in msg or "submitted" in msg or "success" in msg, f"Expected success review message. Got: {msg!r}"

@pytest.mark.functional
def test_review_too_short_validation(driver, helpers, creds):
    """
    Optional negative: review text too short should trigger validation.
    """
    helpers.login(creds["email"], creds["password"])
    helpers.open(PDP_PATH)

    for css in ["a[href='#tab-review']", "a[data-toggle='tab'][href*='review']", "li a[href*='review']"]:
        tabs = driver.find_elements(By.CSS_SELECTOR, css)
        if tabs:
            tabs[0].click()
            break

    name_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#input-name, input[name='name'], input#name"))
    )
    review_textarea = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#input-review, textarea[name='text'], textarea#review"))
    )

    name_input.clear()
    name_input.send_keys("Sizhe")
    review_textarea.clear()
    review_textarea.send_keys("Too short")

    submit = None
    for css in ["#button-review", "button#button-review", "input[value='Continue']", "button[type='submit']"]:
        elems = driver.find_elements(By.CSS_SELECTOR, css)
        if elems:
            submit = elems[0]
            break
    assert submit
    submit.click()

    msg = helpers.success_or_warning_text().lower()
    assert "warning" in msg or "error" in msg or "length" in msg, f"Expected validation for short review. Got: {msg!r}"
