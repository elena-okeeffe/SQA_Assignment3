import os
import pytest
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

DEFAULT_BROWSER = os.environ.get("EP_BROWSER", "chrome").lower()
HEADLESS = os.environ.get("EP_HEADLESS", "1") not in ("0", "false", "False")


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    
def _chrome_driver():
    opts = ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


@pytest.fixture(scope="session")
def base_url():
    return "https://ecommerce-playground.lambdatest.io/" 

@pytest.fixture(params=["chrome"], scope="session")
def browser_name(request):
    bn = os.environ.get("EP_BROWSER")
    if bn:
        return bn.lower()
    return request.param

@pytest.fixture(scope="function")
def driver(request, browser_name):
    if browser_name == "chrome":
        driver = _chrome_driver()
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    driver.implicitly_wait(5)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass
