import pytest
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

HOME_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=common/home"

# Tunable parameters to keep runtime bounded and fail fast
NAV_QUICK_WAIT = 1.0         # short poll interval for quick checks
BREADCRUMB_QUICK_WAIT = 1.0  # seconds to poll for breadcrumb presence on product pages
MAX_PRODUCTS = 10            # check at most this many products from the Asus listing

@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,900")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--log-level=3")

    # Block heavy resources to speed loads
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.stylesheets": 2,
        "profile.managed_default_content_settings.css": 2,
        "profile.managed_default_content_settings.fonts": 2,
    }
    options.add_experimental_option("prefs", prefs)
    options.set_capability("pageLoadStrategy", "eager")

    drv = Chrome(options=options)
    yield drv
    drv.quit()

def js_click(driver, el):
    driver.execute_script("arguments[0].click();", el)

def find_asus_link_from_megamenu(driver):
    """
    From the home page, try to reach the Asus listing by:
      1) Locate Asus anchor in the nav (visible in DOM) and click,
      2) If not present, hover top-level menu areas to reveal the mega menu and try again,
      3) Use JS click fallback where necessary.
    Returns True if a navigation that looks like the Asus listing was initiated.
    """
    # Try direct Asus link in nav
    asus_xpath = "//nav//a[normalize-space() = 'Asus' or contains(normalize-space(.), 'Asus')]"
    try:
        elems = driver.find_elements(By.XPATH, asus_xpath)
        if elems:
            try:
                elems[0].click()
            except WebDriverException:
                js_click(driver, elems[0])
            return True
    except Exception:
        pass

    # Hover common nav containers to reveal mega menu, then retry
    nav_selectors = ["nav#menu", "nav.navbar", "nav"]
    for sel in nav_selectors:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, sel)
            if not containers:
                continue
            # Hover container to trigger mega-menu (if it uses hover)
            try:
                ActionChains(driver).move_to_element(containers[0]).perform()
            except Exception:
                pass
            # brief pause for DOM to update
            time.sleep(0.2)
            elems = driver.find_elements(By.XPATH, asus_xpath)
            if elems:
                try:
                    elems[0].click()
                except WebDriverException:
                    js_click(driver, elems[0])
                return True
        except Exception:
            continue

    # Fallback: try to find Asus link anywhere (manufacturer or category) and click
    try:
        fallback = driver.find_elements(By.XPATH, "//a[contains(., 'Asus') and (contains(@href,'manufacturer') or contains(@href,'category') or contains(@href,'product') )]")
        if fallback:
            try:
                fallback[0].click()
            except WebDriverException:
                js_click(driver, fallback[0])
            return True
    except Exception:
        pass

    return False

def collect_product_links_on_listing(driver):
    """
    Find product links on the current listing/manufacturer page.
    Returns list of hrefs in document order (may be empty).
    """
    selectors = [
        "div.product-layout a[href*='product']",
        "div.product-thumb a[href*='product']",
        "div.product-item a[href*='product']",
        ".product-grid .product a[href*='product']",
        "#content a[href*='product']",
        "a[href*='product/product']"
    ]
    links = []
    seen = set()
    for sel in selectors:
        elems = driver.find_elements(By.CSS_SELECTOR, sel)
        for e in elems:
            href = e.get_attribute("href")
            if href and href not in seen:
                seen.add(href)
                links.append(href)
        if links:
            break
    return links

def get_breadcrumb_text_quick(driver):
    """
    Try to get breadcrumb text synchronously; poll briefly up to BREADCRUMB_QUICK_WAIT seconds.
    Returns breadcrumb string or empty string if not found quickly.
    """
    end = time.time() + BREADCRUMB_QUICK_WAIT
    while time.time() < end:
        elems = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb, ol.breadcrumb, div.breadcrumb")
        if elems:
            text = elems[0].text.strip()
            if text:
                return text
        time.sleep(0.1)
    return ""

def test_megamenu_laptops_asus_breadcrumbs_from_home(driver):
    # 1) Start at home
    driver.get(HOME_URL)

    # 2) Navigate via Mega Menu -> Laptops -> Asus (resilient)
    navigated = find_asus_link_from_megamenu(driver)
    if not navigated:
        pytest.fail("Unable to find or click Asus link from the Mega Menu on the home page")

    # Small quick wait for the listing to appear (we use quick polling only)
    start = time.time()
    while time.time() - start < NAV_QUICK_WAIT:
        # check for listing container or breadcrumb presence
        if driver.find_elements(By.CSS_SELECTOR, "#content, ul.breadcrumb, div.breadcrumb"):
            break
        time.sleep(0.1)
    else:
        # give a slightly longer second chance
        time.sleep(0.5)

    # 3) Collect product links on the resulting listing page
    product_links = collect_product_links_on_listing(driver)
    assert product_links, "No product links found on Asus listing page after navigating via Mega Menu"

    # 4) Visit each product up to MAX_PRODUCTS and fail on first breadcrumb mismatch
    expected_terms = ["Laptops", "Asus"]
    for idx, href in enumerate(product_links[:MAX_PRODUCTS], start=1):
        try:
            driver.get(href)
        except WebDriverException as e:
            pytest.fail(f"Product #{idx} at {href} failed to load: {e}")

        breadcrumb = get_breadcrumb_text_quick(driver)
        if not breadcrumb:
            pytest.fail(f"Product #{idx} at {href} did not return a breadcrumb quickly")

        # If missing expected terms, fail and include the full breadcrumb text
        missing = [t for t in expected_terms if t not in breadcrumb]
        if missing:
            pytest.fail(f"Product #{idx} breadcrumbs did not contain \"Asus\" and/or \"Laptops\". Full breadcrumb: '{breadcrumb}'")

    # 5) success message if all checked products passed
    checked = min(len(product_links), MAX_PRODUCTS)
    success_message = f"SUCCESS: All {checked} products contain both {expected_terms[0]} and {expected_terms[1]} in breadcrumbs"
    print(success_message)
    assert True, success_message