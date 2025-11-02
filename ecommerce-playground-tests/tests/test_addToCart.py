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
    """Initialize Chrome WebDriver"""
    opts = Options()
    opts.add_argument("--window-size=1600,1000")
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    yield drv
    drv.quit()


def test_add_to_cart_function(driver):
    """
    Function Name: Add to Cart Function
    Objective: Verify that the product selected from the homepage is correctly added to the shopping cart.
    """

    home = HomePage(driver, BASE_URL)
    home.open()

    product_name = "HTC Touch HD"
    product_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, product_name))
    )
    product_link.click()

    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "button-cart"))
    )
    add_button.click()

    success_toast = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.alert.alert-success.alert-dismissible")
        )
    )

    assert product_name in success_toast.text, (
        f"Expected '{product_name}' in success message, but got: {success_toast.text}"
    )

    print(f" Add to Cart successful for product: {product_name}")
