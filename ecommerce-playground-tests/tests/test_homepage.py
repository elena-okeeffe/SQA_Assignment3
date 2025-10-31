import pytest
from pages.home_page import HomePage

def test_homepage_loads(driver, base_url):
    home = HomePage(driver, base_url)
    home.open()

    # Title check
    title = home.title()
    assert title is not None and len(title) > 0

    # Check featured products with diagnostics
    has_products = home.has_featured_products()
    if not has_products:
        print("DIAG: url=", driver.current_url)
        print("DIAG: title=", driver.title)
        print("DIAG: snapshot (first 3000 chars) =", driver.page_source[:3000])
    assert has_products

    # Success message for visibility in CI or local runs
    print("TEST SUCCESS: test_homepage_loads passed — homepage loaded and featured products found.")