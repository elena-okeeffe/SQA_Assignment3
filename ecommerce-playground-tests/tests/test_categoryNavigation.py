import pytest
from pages.home_page import HomePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://ecommerce-playground.lambdatest.io/"

@pytest.fixture(scope="session")
def driver():
    """Initialize Chrome WebDriver."""
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    drv.quit()

def test_category_navigation_function(driver):
    """
    Function: Category Navigation
    Goal: Each link under 'Shop by Category' opens a category/product page
          (some known-broken ones currently return to the homepage).
    """
    home = HomePage(driver, BASE_URL)
    home.open()


    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Shop by Category"))
    ).click()


    panel = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div#widget-navbar-217834 ul.list-unstyled")
        )
    )

    names = [a.text.strip() for a in panel.find_elements(By.TAG_NAME, "a") if a.text.strip()]
    assert names, "No categories found in 'Shop by Category' panel."


    expected_working = {"Components", "Cameras", "Phones & PDAs", "Laptops & Notebooks"}
    expected_failing = {
        "Fashion and Accessories",
        "Beauty and Saloon",
        "Autoparts and Accessories",
        "Washing machine",
        "Gaming consoles",
    }

    for name in names:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Shop by Category"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div#widget-navbar-217834 ul.list-unstyled")
            )
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, name))
        ).click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        url = driver.current_url

        if name in expected_working:
            assert ("category" in url) or ("product" in url), (
                f"{name}: expected category/product page, got URL: {url}"
            )
        elif name in expected_failing:
            assert "route=common/home" in url, (
                f"{name}: expected current buggy behavior (homepage). "
                f"If this fails, the bug may be fixed. URL: {url}"
            )
        else:
            assert any(k in url for k in ("category", "product", "route=common/home")), (
                f"{name}: unexpected URL pattern: {url}"
            )
