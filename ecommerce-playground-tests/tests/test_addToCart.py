import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from pages.home_page import HomePage

BASE_URL = "https://ecommerce-playground.lambdatest.io"

pytest.fixture(scope="session")
def driver():
    """Initialize Chrome WebDriver"""
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    # Uncomment if you want headless mode:
    # opts.add_argument("--headless=new")
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    drv.quit()


def test_add_to_cart_function(driver):
    """
    Function Name: Add to Cart Function
    Objective: Verify that the product selected from the homepage is correctly added to the shopping cart.
    """

    # Step 1: Open the website using HomePage object
    home = HomePage(driver, BASE_URL)
    home.open()

    # Step 2: Scroll to a visible product and click its name to open the product page
    product_name = "HTC Touch HD"
    product_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, product_name))
    )
    product_link.click()

    # Step 3: Click the "Add to Cart" button on the Product Detail Page (PDP)
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "button-cart"))
    )
    add_button.click()

    # Step 4: Wait for the success message (toast alert)
    success_toast = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.alert.alert-success.alert-dismissible")
        )
    )

    # Step 5: Verify that the correct product name appears in the success message
    assert product_name in success_toast.text, (
        f"Expected '{product_name}' in success message, but got: {success_toast.text}"
    )

    print(f" Add to Cart successful for product: {product_name}")
