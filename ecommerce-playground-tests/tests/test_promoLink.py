import pytest
from pages.home_page import HomePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://ecommerce-playground.lambdatest.io"


@pytest.fixture(scope="session")
def driver():
    """Initialize Chrome WebDriver."""
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    drv.quit()


def test_promotion_link_washing_machine(driver):
    """
    Function: Promotional Link Function
    Goal: Verify the 'Shop Now' button in the 'Up to 50% Off on Fully Automatic Top Load Washing Machine'
          promotion navigates correctly.

    Current site behavior (bug you observed):
      - Clicking the 'Shop Now' button returns to the homepage instead of a category/product page.
    This test asserts the current buggy behavior so it documents the defect. If the site is fixed later,
    change the assertion to check for 'category' in the URL.
    """

    home = HomePage(driver, BASE_URL)
    home.open()

    driver.execute_script("window.scrollBy(0, 1200);")

    promo_heading_locator = (
        By.XPATH,
        "//h3[contains(translate(., 'UPTO', 'upto'), 'upto 50% off') and "
        "contains(translate(., 'WASHING MACHINE', 'washing machine'), 'washing machine')]"
    )
    heading = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(promo_heading_locator)
    )

    shop_now = heading.find_element(By.XPATH, ".//following::a[normalize-space()='SHOP NOW'][1]")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(shop_now))
    shop_now.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    url = driver.current_url

    assert "route=common/home" in url, (
        "Expected current buggy behavior (homepage redirect). "
        "If this assertion fails, the link may have been fixed; "
        f"update the test to assert 'category' in URL. URL: {url}"
    )


@pytest.mark.xfail(reason="Expected correct behavior after bug is fixed")
def test_promotion_link_washing_machine_expected_after_fix(driver):
    """
    Same scenario as above, but expresses the correct expectation for when the site is fixed.
    This test is marked xfail for now.
    """
    home = HomePage(driver, BASE_URL)
    home.open()
    driver.execute_script("window.scrollBy(0, 1200);")

    promo_heading_locator = (
        By.XPATH,
        "//h3[contains(translate(., 'UPTO', 'upto'), 'upto 50% off') and "
        "contains(translate(., 'WASHING MACHINE', 'washing machine'), 'washing machine')]"
    )
    heading = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(promo_heading_locator)
    )
    shop_now = heading.find_element(By.XPATH, ".//following::a[normalize-space()='SHOP NOW'][1]")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(shop_now))
    shop_now.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    url = driver.current_url

    assert ("category" in url) or ("product" in url), f"Expected category/product page; got {url}"